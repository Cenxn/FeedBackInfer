from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json
import os
import pandas as pd
import numpy as np
import random
import string
from celery import chord
from upload_essay.src.configuration import CFG
from upload_essay.tasks import inference_single_csv, distribute_csv_file_no_generate, process_csv_paths


def type_essay(request):
    if request.method == 'GET':
        return render(request, 'index.html')


@csrf_exempt
def submit_discourse(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        essay_id = data['essay_id']
        entries = data['entries']

        df = pd.DataFrame(entries)
        df['essay_id'] = essay_id  # Add the same essay_id to all entries

        # Make sure the DataFrame contains all the required columns
        df = df.rename(columns={
            'discourse': 'discourse_text',
            'type': 'discourse_type'
        })
        df['discourse_id'] = df.apply(lambda row: generate_id(), axis=1)

        df = df[['discourse_id', 'essay_id', 'discourse_text', 'discourse_type']]

        # Store to static file path
        static_csv_path = CFG.GENERATED_CSV_PATH
        static_essay_path = CFG.GENERATED_ESSAY_PATH

        if not os.path.exists(static_csv_path):
            os.makedirs(static_csv_path)
        file_path = os.path.join(static_csv_path, f'{essay_id}_chunk.csv')
        df.to_csv(file_path, index=False)

        sample = df[['discourse_id', 'discourse_text']].copy()
        sample['Ineffective'] = np.nan
        sample['Adequate'] = np.nan
        sample['Effective'] = np.nan
        sample_csv_path = os.path.join(static_csv_path, f'{essay_id}_sample.csv')
        sample.to_csv(sample_csv_path, index=False)

        txt_file_path = os.path.join(static_essay_path, f'{essay_id}.txt')
        essay_content = '\n'.join(df['discourse_text'])
        with open(txt_file_path, 'w') as file:
            file.write(essay_content)

        print(f'Generated [{file_path}], sample saved [{sample_csv_path}] and essay [{txt_file_path}]')

        process_csv_result = inference_single_csv.s(df_path=file_path,
                                                    essay_folder_path=static_essay_path,
                                                    output_csv_path=sample_csv_path
                                                    ).delay()

        generated_file_path = process_csv_result.get()

        print(f'[Analyzed finished] Result at [{generated_file_path}]')

        html_table = pd.read_csv(generated_file_path).to_html(index=False)

        return JsonResponse({
            'status': 'success',
            'essay_id': essay_id,
            'html_table': html_table,
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)


def generate_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))


def upload_csv(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        # Read uploaded CSV file
        print('[Check] Start check file format')
        try:
            df = pd.read_csv(csv_file)
        except pd.errors.ParserError:
            return JsonResponse({'status': 'error', 'error': 'Invalid CSV file!'}, status=400)

        # Check attributes in csv file
        required_columns = ['discourse_id', 'essay_id', 'discourse_text', 'discourse_type']
        if not all(col in df.columns for col in required_columns):
            return JsonResponse({'status': 'error', 'error': 'CSV file is missing required columns. \n '
                                          'Require:["discourse_id", "essay_id", "discourse_text", "discourse_type"]'}, status=400)
        print('[Check-pass] Have request attribute')

        # Check whether discourse_type contains necessary value
        valid_discourse_types = ['Lead', 'Position', 'Claim', 'Evidence',
                                 'Concluding Statement', 'Counterclaim', 'Rebuttal']
        invalid_discourse_types = df[~df['discourse_type'].isin(valid_discourse_types)]['discourse_type'].unique()
        if len(invalid_discourse_types) > 0:
            return JsonResponse({'status': 'error', 'error': f'Invalid discourse types: {", ".join(invalid_discourse_types)}'}, status=400)
        print('[Check-pass] Have request discourse_type')

        # Check if essay_id contains more than 20 unique values
        unique_essay_ids = df['essay_id'].nunique()
        if unique_essay_ids > 20:
            return JsonResponse({
                    'status': 'error',
                    'error': 'The number of unique essay_id values exceeds 20. '
                             'Please use Celery directly instead of this Django web app, '
                             'as it may take too long to process.'},
                status=400)
        print('[Check-pass] Have appropriate num of essay ')

        upload_dir = CFG.GENERATED_CSV_PATH
        generate_essay_path = CFG.GENERATED_ESSAY_PATH
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        upload_path = os.path.join(upload_dir, csv_file.name)
        with open(upload_path, 'wb') as destination:
            for chunk in csv_file.chunks():
                destination.write(chunk)

        processed_file_path = process_csv(upload_path, generate_essay_path)
        html_table = pd.read_csv(processed_file_path).to_html(index=False)

        return JsonResponse({'status': 'success', 'html_table': html_table})

    if request.method == 'GET':
        return render(request, 'upload.html')


def process_csv(csv_file_path, output_directory):
    df = pd.read_csv(csv_file_path)
    grouped = df.groupby('essay_id')

    for essay_id, group in grouped:
        file_name = f"{essay_id}.txt"
        file_path = os.path.join(output_directory, file_name)

        with open(file_path, 'w', encoding='utf-8') as file:
            for _, row in group.iterrows():
                discourse_text = row['discourse_text']
                file.write(f"{discourse_text}\n")
        print(f"Text file {file_path} generated successfully.")

    distribute_task = distribute_csv_file_no_generate.s(df_path=csv_file_path, essay_path=output_directory).delay()
    group = (
        [inference_single_csv.s(chunk_df_path, essay_path, sample_df_path)
         for chunk_df_path, essay_path, sample_df_path in distribute_task.get()]
    )
    print(f"[Executing] Generated result from distribute_csv_file_no_generate and prepare_inference_tasks.")
    result_chord = chord(group)(process_csv_paths.s())
    final_result = result_chord.get()
    print(f"[FINISH] Workflow executed. Output file at {final_result}")

    return final_result

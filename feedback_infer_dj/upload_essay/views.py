from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json
import os
import pandas as pd
import numpy as np
from .src.configuration import CFG
from .tasks import inference_single_csv


def type_essay(request):
    if request.method == 'GET':
        return render(request, 'index.html')


@csrf_exempt
def submit_discourse(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        essay_id = data['essay_id']
        entries = data['entries']

        # 创建 DataFrame
        df = pd.DataFrame(entries)
        df['essay_id'] = essay_id  # 为所有条目添加相同的 essay_id

        # 确保 DataFrame 包含所有所需列
        df = df.rename(columns={
            'discourse': 'discourse_text',
            'type': 'discourse_type'
        })
        df['discourse_id'] = df.apply(lambda row: generate_id(), axis=1)

        df = df[['discourse_id', 'essay_id', 'discourse_text', 'discourse_type']]

        # 存储到静态文件路径
        # static_csv_path = 'static/downloads'
        # static_essay_path = 'static/downloads'
        static_csv_path = CFG.GENERATED_CSV_PATH
        static_essay_path = CFG.GENERATED_ESSAY_PATH

        if not os.path.exists(static_csv_path):
            os.makedirs(static_csv_path)
        file_path = os.path.join(static_csv_path, f'{essay_id}_chunk.csv')
        df.to_csv(file_path, index=False)

        sample = df[['discourse_id']].copy()
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

        # 生成可访问的 URL
        download_csv_url = f'/static/downloads/{essay_id}_chunk.csv'
        download_sam_url = f'/static/downloads/{essay_id}_sample.csv'

        return JsonResponse({
            'status': 'success',
            'essay_id': essay_id,
            'download_csv_url': download_csv_url,
            'download_reuslt_url': download_sam_url
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)


def generate_id():
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
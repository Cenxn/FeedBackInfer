function addInput() {
    const container = document.getElementById('input-container');
    const inputGroup = document.createElement('div');
    inputGroup.className = 'input-group';

    const textarea = document.createElement('textarea');
    textarea.placeholder = 'Enter discourse';
    textarea.rows = '4';
    textarea.cols = '50';

    const select = document.createElement('select');
    const options = ['Lead', 'Position', 'Claim', 'Evidence', 'Concluding Statement'];
    options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt;
        option.textContent = opt;
        select.appendChild(option);
    });

    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Delete';
    deleteButton.onclick = function() {
        container.removeChild(inputGroup);
    };

    inputGroup.appendChild(textarea);
    inputGroup.appendChild(select);
    inputGroup.appendChild(deleteButton);
    container.appendChild(inputGroup);
}

document.getElementById('discourse-form').onsubmit = function(event) {
    event.preventDefault(); // 阻止表单的默认提交行为
    showLoading(true);

    const groups = document.querySelectorAll('.input-group');
    const data = Array.from(groups).map((group, index) => {
        const textarea = group.querySelector('textarea');
        const select = group.querySelector('select');
        return {
            discourse_id: generateID(),
            discourse: textarea.value,
            type: select.value
        };
    });

    const submission = {
        essay_id: generateID(12),
        entries: data
    };

    fetch('/submit-discourse', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(submission)
    }).then(response => response.json())
      .then(data => {
          showLoading(false);
          if (data.status === 'success') {
              const link = document.getElementById('download-link');
              link.innerHTML = `<a href="${data.download_csv_url}">Download your reuslt file</a> <a href="${data.download_reuslt_url}">Download your result file</a>`;
              link.style.display = 'block';
          } else {
              console.error('Error:', data.message);
          }
      })
      .catch(error => {
          console.error('Error:', error);
          showLoading(false);
      });
};

function showLoading(show) {
    const loading = document.getElementById('loading');
    loading.style.display = show ? 'block' : 'none';
}

function generateID(length = 12) {
    return [...Array(length)].map(() => Math.floor(Math.random() * 16).toString(16).toUpperCase()).join('');
}


window.onload = function() {
    addInput(); // 确保在页面加载时就添加一个输入框
};

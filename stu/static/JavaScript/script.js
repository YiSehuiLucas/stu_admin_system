document.addEventListener('DOMContentLoaded', function () {
    // 获取 DOM 元素
    const openModalBtn = document.getElementById('openModalBtn');
    const modal = document.getElementById('myModal');
    const closeBtn = document.querySelector('.close');
    const applicationForm = document.getElementById('applicationForm');
    const submitBtn = document.getElementById('submitBtn');
    const courseSelect = document.getElementById('course_tch');

    // 打开模态框
    openModalBtn.addEventListener('click', () => {
        modal.style.display = 'block';
        document.body.classList.add('modal-open'); // 添加 modal-open 类
    });

    // 关闭模态框
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
        document.body.classList.remove('modal-open'); // 移除 modal-open 类
    });

    // 点击模态框外部关闭
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
            document.body.classList.remove('modal-open'); // 移除 modal-open 类
        }
    });

    // 处理表单提交按钮点击事件
    submitBtn.addEventListener('click', (event) => {
        event.preventDefault(); // 阻止默认行为

        // 获取选中的课程 ID 和教师 ID
        const courseOption = courseSelect.options[courseSelect.selectedIndex];
        const course_id = courseOption.value;
        const teacher_id = courseOption.text.split('-')[1].trim().split('(')[1].split(')')[0].split('-')[0];

        // 获取申请理由
        const messagej = document.getElementById('message').value;

        // 检查是否选择了课程
        if (!course_id || !teacher_id) {
            alert('请选择一个课程');
            return;
        }

        // 检查是否填写了申请理由
        if (!messagej) {
            alert('请填写申请理由');
            return;
        }

        // 显示获取到的值（可以根据需要修改为其他操作）
        console.log('课程 ID:', course_id);
        console.log('教师 ID:', teacher_id);
        console.log('申请理由:', messagej);

        // 提交表单
        applicationForm.submit();
    });
});
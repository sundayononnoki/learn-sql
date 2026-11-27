const form = document.querySelector('#query-check');
const feedback = document.querySelector('#query-feedback');

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const choice = new FormData(form).get('first_product');
  if (!choice) {
    feedback.textContent = '先选一个编号，再核对。';
    return;
  }
  feedback.textContent = choice === '2'
    ? '答对了。2 和 5 同价，编号 2 在升序排列中排在前面。'
    : '再数一次。先只保留图书，然后找最高价。并列时，用编号升序。';
});

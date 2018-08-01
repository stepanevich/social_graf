var userAutocomplete = function() {
  $('#user_autocomplete').autocomplete({
      autoFocus: true,
      source: '/autocomplete',
      minLength: 3
  });
}

var checkInProgress = function() {
  mark = $('.inprogress')
  if (mark && mark.length) {
    checkStatus();
  }
}

checkStatus = function() {
  user_id = $('div[data-user-id]').data('user-id');
  target_user_id = $('div[data-target-user-id]').data('target-user-id');
  sendRequest = setInterval((function() {
    $.get('/check_status', { user_id: user_id, target_user_id: target_user_id })
      .done(function(data) {
        if (data.status == 'found') {
          clearInterval(sendRequest);
          $.get('/show_results_table', { user_id: user_id, target_user_id: target_user_id })
            .done(function(html) {
              $('#message').html('Ура! Найдены общие знакомые');
              $('#results-table').html(html);
            })
        } else if (data.status == 'fail' || data.status == 'notfound') {
          clearInterval(sendRequest);
          $('#message').html('Увы, но общих знакомых нет');
        } else if (data.status == null) {
          clearInterval(sendRequest);
          window.location = '/search_user';
          alert('Данные по этой паре пользователей устарели. Повторите запрос');
        }
      });
  }), 5000);
}


$(document).ready(function() {
  userAutocomplete();
  checkInProgress();
});

var apigClient = apigClientFactory.newClient({
  accessKey: 'ACCESS_KEY',
  secretKey: 'SECRET_KEY',
});
var checkout = {};

// var params = {};
// var body = {
//   messages: [
//     {
//       type: 'string',
//       unstructured: {
//         id: 'string',
//         text: 'string',
//         timestamp: 'string',
//       },
//     },
//   ],
// };
// apigClient
//   .chatbotPost(params, body, {})
//   .then(function (result) {
//     // Add success callback code here.
//     console.log('fff');
//   })
//   .catch(function (result) {
//     // Add error callback code here.
//   });

$(document).ready(function () {
  var $messages = $('.messages-content'),
    d,
    h,
    m,
    i = 0;

  $(window).load(function () {
    $messages.mCustomScrollbar();
    insertResponseMessage(
      "Hi there, I'm your personal Concierge. How can I help you today?"
    );
  });

  function updateScrollbar() {
    $messages
      .mCustomScrollbar('update')
      .mCustomScrollbar('scrollTo', 'bottom', {
        scrollInertia: 10,
        timeout: 0,
      });
  }

  function setDate() {
    d = new Date();
    if (m != d.getMinutes()) {
      m = d.getMinutes();
      $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo(
        $('.message:last')
      );
    }
  }

  // function callChatbotApi(message) {
  //   // params, body, additionalParams
  //   return apigClient.chatbotPost(
  //     {},
  //     {
  //       messages: [
  //         {
  //           type: 'unstructured',
  //           unstructured: {
  //             text: message,
  //           },
  //         },
  //       ],
  //     },
  //     {}
  //   );
  // }

  function insertMessage() {
    msg = $('.message-input').val();
    if ($.trim(msg) == '') {
      return false;
    }
    $('<div class="message message-personal">' + msg + '</div>')
      .appendTo($('.mCSB_container'))
      .addClass('new');
    setDate();
    $('.message-input').val(null);
    updateScrollbar();
    var body = {
      "messages": [
          {
              "type": "unstructured",
              "unstructured": {
                  "user_id": "111",
                  "text": msg,
                  "time": new Date().toISOString()
              }
          }
      ]
  };
    apigClient.chatbotPost({},body,{})
      .then((response) => {
        console.log(response.data);
        var data = response.data.body;
        //console.log(data.messages);
        if (data.messages && data.messages.length > 0) {
          console.log('received ' + data.messages.length + ' messages');

          var messages = data.messages;

          for (var message of messages) {
            if (message.type === 'unstructured') {
              insertResponseMessage(message.unstructured.text);
            } else if (
              message.type === 'structured' &&
              message.structured.type === 'product'
            ) {
              var html = '';

              insertResponseMessage(message.structured.text);

              setTimeout(function () {
                html =
                  '<img src="' +
                  message.structured.payload.imageUrl +
                  '" witdth="200" height="240" class="thumbnail" /><b>' +
                  message.structured.payload.name +
                  '<br>$' +
                  message.structured.payload.price +
                  '</b><br><a href="#" onclick="' +
                  message.structured.payload.clickAction +
                  '()">' +
                  message.structured.payload.buttonLabel +
                  '</a>';
                insertResponseMessage(html);
              }, 1100);
            } else {
              console.log('not implemented');
            }
          }
        } else {
          insertResponseMessage(
            'Oops, something went wrong. Please try again.'
          );
        }
      })
      .catch((error) => {
        console.log('an error occurred', error);
        insertResponseMessage('Oops, something went wrong. Please try again.');
      });
  }

  $('.message-submit').click(function () {
    insertMessage();
  });

  $(window).on('keydown', function (e) {
    if (e.which == 13) {
      insertMessage();
      
      return false;
    }
  });

  function insertResponseMessage(content) {
    $(
      '<div class="message loading new"><figure class="avatar"><img src="https://media.tenor.com/images/4c347ea7198af12fd0a66790515f958f/tenor.gif" /></figure><span></span></div>'
    ).appendTo($('.mCSB_container'));
    updateScrollbar();

    setTimeout(function () {
      $('.message.loading').remove();
      $(
        '<div class="message new"><figure class="avatar"><img src="https://media.tenor.com/images/4c347ea7198af12fd0a66790515f958f/tenor.gif" /></figure>' +
          content +
          '</div>'
      )
        .appendTo($('.mCSB_container'))
        .addClass('new');
      setDate();
      updateScrollbar();
      i++;
    }, 500);
    updateScrollbar();

  }
});

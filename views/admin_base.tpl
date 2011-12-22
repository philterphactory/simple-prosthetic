<html>
    <head>
        <title>{{title}}</title>
        <style>
.message_success, .message_error, .message_warning {
    margin: .5em;
    padding: .7em;
}
.message_success {
    border: 1px outset #0c0;
    background-color: #6f6;
}
.message_error {
    border: 1px outset #c00;
    background-color: #f66;
}
.message_warning {
    border: 1px outset #00c;
    background-color: #66f;
}
thead tr td {
    font-weight: bold;
}
        </style>
    </head>
    <body>
        <ul class="menu">
            <li><a href="/">Home</a></li>
            <li><a href="/admin/">Admin</a></li>
        </ul>
        <h1>{{title}}</h1>
%if flash[0] and flash[1]:
    <div class="message_{{flash[0]}}">{{flash[1]}}</div>
%end
%include
    </body>
</html>

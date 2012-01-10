<html>
    <head>
        <title>{{title}}</title>
        <link rel="stylesheet" type="text/css" href="/static/style.css" type="text/css" />
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

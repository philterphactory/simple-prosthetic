%rebase admin_base title='%s Admin' % kindname, flash=flash

<ul>
    <li><a href="/admin/{{kindname}}/add/">Add</a></li>
</ul>
<table border="1" cellpadding="5">
    <thead>
        <tr>
            <td>key</td>
%for p in sorted(kind.properties()):
            <td>{{p.capitalize()}}</td>
%end
            <td>Actions</td>
        </tr>
    </thead>
    <tbody>
%for instance in kind.all():
%name = instance.key().name()
        <tr>
            <td><a href="/admin/{{kindname}}/edit/{{name}}/">{{name}}</td>
%for p in sorted(kind.properties()):
            <td>{{getattr(instance, p, None)}}</td>
%end
            <td>
                <a href="/admin/{{kindname}}/edit/{{name}}/">edit</a> |
                <a href="/admin/{{kindname}}/delete/{{name}}/">delete</a>
            </td>
        </tr>
%end
    </tbody>
</table>

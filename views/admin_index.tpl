%rebase admin_base title='Simple Prosthetic Admin', flash=flash
<ul>
%for kind in kinds:
    <li><a href="/admin/{{kind}}/">Manage {{kind}} entities</li>
%end
</ul>

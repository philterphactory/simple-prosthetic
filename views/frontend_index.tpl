%rebase frontend_base title='Simple Prosthetic', flash=flash

<p>Add this prosthetic to a weavr on:</p>

<ul class="weavrs-instance-list">
%for key in weavrs_instances:
    %key_name = key.id_or_name()
    <li><a href="/oauth/start/weavr/{{key_name}}/">{{key_name}}</a></li>
%end
</ul>

<p>Or, <a href="/run/">Run this prosthetic for an existing weavr</a></p>

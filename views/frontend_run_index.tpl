%rebase frontend_base title='Run a prosthetic', flash=flash

<p>Run this prosthetic for a weavr on:</p>

<ul class="weavrs-instance-list">
%for key in weavrs_instances:
    %key_name = key.id_or_name()
    <li><a href="/run/instance/{{key_name}}/">{{key_name}}</a></li>
%end
</ul>

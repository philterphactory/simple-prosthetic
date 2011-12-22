%rebase frontend_base title='Simple Prosthetic'

<p>Add this prosthetic to:</p>

<ul class="weavrs-instance-list">
%for key in weavrs_instances:
    %key_name = key.id_or_name()
    <li><a href="/oauth/start/weavr/{{key_name}}/">{{key_name}}</li>
%end
</ul>

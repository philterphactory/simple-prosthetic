%rebase admin_base title='%s %s %s' % (edit and 'Edit' or 'Add New', kindname, edit and name or ''), flash=flash

<style>
.form_wrapper {
    text-align: center;
}
form {
    text-align: left;
    display: inline-block;
    border: 1px outset #aaa;
    padding: 1em;
    background-color: #eee;
}
label {
    display: inline-block;
    width: 175px;
}
.form_action_section {
    text-align: center;
}
.required {
    font-weight: bold;
}
</style>
<div class="form_wrapper">
    <form method="POST" action="" enctype="multipart/form-data">
        <div class="form_key_section">
            <h2>Key</h2>
%for p in kind.Meta.key_parts:
    %label_name = 'label__p__key__%s' % p
    %input_name = 'input__p__key__%s' % p
    %input_value = p in values and values.get(p) or ''
            <div class="form_row">
%if edit:
                <span class="required">{{p}}:</span> {{input_value}}
%else:
                <label
                        id="{{label_name}}"
                        for="{{input_name}}"
                        class="required">
                {{p}}:
                </label>
                <input
                        type="text"
                        id="{{input_name}}"
                        name="{{input_name}}"
                        value="{{input_value}}">
%end
            </div>
%end
        </div>
        <div class="form_property_section">
            <h2>Properties</h2>
%for p in sorted(kind.properties()):
%label_name = 'label__p__%s' % p
%input_name = 'input__p__%s' % p
%input_value = p in values and values.get(p) or ''
%label_class_attr = kind._properties[p].required and 'class="required"' or ''
            <div class="form_row">
                <label
                        id="{{label_name}}"
                        for="{{input_name}}"
                        {{!label_class_attr}}
                        >
                {{p}}:
                </label>
                <input
                        type="text"
                        id="{{input_name}}"
                        name="{{input_name}}"
                        value="{{input_value}}">
            </div>
%end
        </div>
        <div class="form_action_section">
            <input type="submit" name="submit" value="Submit">
        </div>
    </form>
</div>

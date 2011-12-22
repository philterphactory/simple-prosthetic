%rebase admin_base title='Delete %s %s' % (kindname, key), flash=flash

<p>Are you sure you wish to delete {{kindname}} {{key}}?</p>

<form method="POST" action="" enctype="multipart/form-data">
    <input type="submit" value="Yes, delete it">
</form>
<p><a href="javascript:history.go(-1)">Cancel</a></p>

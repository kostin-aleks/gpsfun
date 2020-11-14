from PIL import Image

def manage_files(request, instance, file_class, image_class):
    data = request.POST
    files = request.FILES

    if files:
        filename = request.FILES['upload_file'].name
        try:
            img = Image.open(request.FILES['upload_file'])
            image_class(refobject = instance,
                        filename=filename,
                        image = request.FILES['upload_file']).save()
        except IOError:
            file_class(refobject = instance,
                       filename=filename,
                       afile = request.FILES['upload_file']).save()


    for addfile_id in data.getlist('add_file'):
        afile = file_class.objects.get(refobject=instance,
                                       id=addfile_id)
        instance.content += '<a href="%s">%s</a>' % (afile.afile.url,
                                                     afile.filename)

    for addimage_id in data.getlist('add_image'):
        image = image_class.objects.get(refobject=instance,
                                        id=addimage_id)
        instance.content += '<img src="%s" />' % image.image.url

    for delfile_id in data.getlist('del_file'):
        afile = file_class.objects.get(refobject=instance,
                                       id=delfile_id)
        old_content = '<a href="%s">%s</a>' % (afile.afile.url,
                                               afile.filename)
        instance.content = instance.content.replace(old_content, '')
        afile.delete()

    for delimage_id in data.getlist('del_image'):
        image = image_class.objects.get(refobject=instance,
                                        id=delimage_id)
        old_content = '<img src="%s" />' % image.image.url
        instance.content = instance.content.replace(old_content, '')
        image.delete()

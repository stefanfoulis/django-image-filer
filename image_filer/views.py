import os
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden,HttpResponseBadRequest
from django.contrib.sessions.models import Session
from django.conf import settings

from models import Folder, FolderRoot, Image, Bucket, BucketItem
from models import tools

from django import forms

class NewFolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ('name', )

def _userperms(item, request):
    r = []
    ps = ['read', 'edit', 'add_children']
    for p in ps:
        attr = "has_%s_permission" % p
        if hasattr(item, attr):
            x = getattr(item, attr)(request)
            if x:
                r.append( p )
    return r
class ImagesWithMissingDataRoot(FolderRoot):
    def _children(self):
        return []
    children = property(_children)
    def _files(self):
        return Image.objects.filter(has_all_mandatory_data=False)
    files = property(_files)
    
    
def directory_listing(request, folder_id=None, images_with_missing_data=False):
    new_folder_form = NewFolderForm()
    if images_with_missing_data:
        folder = ImagesWithMissingDataRoot()
    elif folder_id == None:
        folder = FolderRoot()
    else:
        folder = Folder.objects.get(id=folder_id)
    
    # Debug    
    upload_file_form = UploadFileForm()
    
    folder_children = []
    folder_files = []
    if issubclass(type(folder), FolderRoot):
        for f in folder.children:
            f.perms = _userperms(f, request)
            folder_children.append(f)
        for f in folder.files:
            folder_files.append(f)
    else:
        for f in folder.children.all():
            f.perms = _userperms(f, request)
            if hasattr(f, 'has_read_permission'):
                if f.has_read_permission(request):
                    folder_children.append(f)
            else:
                folder_children.append(f) 
        for f in folder.files:
            f.perms = _userperms(f, request)
            if hasattr(f, 'has_read_permission'):
                if f.has_read_permission(request):
                    folder_files.append(f)
            else:
                folder_files.append(f)
    try:
        permissions = {
            'has_edit_permission': folder.has_edit_permission(request),
            'has_read_permission': folder.has_read_permission(request),
            'has_add_children_permission': folder.has_add_children_permission(request),
        }
    except:
        permissions = {}
    
    #print folder_files
    #print folder_children
    return render_to_response('image_filer/directory_listing.html', {
            'folder':folder,
            'folder_children':folder_children,
            'folder_files':folder_files,
            'new_folder_form': new_folder_form,
            'upload_file_form': upload_file_form,
            'permissions': permissions,
            'permstest': _userperms(folder, request),
            'current_url': request.path,
        }, context_instance=RequestContext(request))

def edit_folder(request, folder_id):
    # TODO: implement edit_folder view
    folder=None
    return render_to_response('image_filer/folder_edit.html', {
            'folder':folder,
        }, context_instance=RequestContext(request))

def edit_image(request, folder_id):
    # TODO: implement edit_image view
    folder=None
    return render_to_response('image_filer/image_edit.html', {
            'folder':folder,
        }, context_instance=RequestContext(request))

def make_folder(request, folder_id=None):
    if folder_id:
        folder = Folder.objects.get(id=folder_id)
    else:
        folder = None
    if request.user.is_superuser:
        pass
    elif folder == None:
        # regular users may not add root folders
        return HttpResponseForbidden()
    elif not folder.has_add_children_permission(request):
        # the user does not have the permission to add subfolders
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        new_folder_form = NewFolderForm(request.POST)
        if new_folder_form.is_valid():
            new_folder = new_folder_form.save(commit=False)
            new_folder.parent = folder
            new_folder.owner = request.user
            new_folder.save()
            return HttpResponseRedirect('')
    else:
        new_folder_form = NewFolderForm()
    return render_to_response('image_filer/include/new_folder_form.html', {
            'new_folder_form': new_folder_form,
    }, context_instance=RequestContext(request))

class UploadFileForm(forms.ModelForm):
    class Meta:
        model=Image
        #fields = ('file',)
        
from image_filer.utils.files import generic_handle_file

def upload(request, folder_id=None):
    """
    receives an upload from the flash uploader and fixes the session
    because of the missing cookie. Receives only one file at the time, 
    althow it may be a zip file, that will be unpacked.
    """
    
    # flashcookie-hack (flash does not submit the cookie, so we send the
    # django sessionid over regular post
    engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
    session_key = request.POST.get('cookieVar')
    request.session = engine.SessionStore(session_key)
    #print request.session.session_key, request.user
    if folder_id:
        folder = Folder.objects.get(id=folder_id)
    else:
        folder = None
    
    # check permissions
    if request.user.is_superuser:
        pass
    elif folder == None:
        # regular users may not add root folders
        return HttpResponseForbidden()
    elif not folder.has_add_children_permission(request):
        # the user does not have the permission to images to this folder
        return HttpResponseForbidden()
    
    # upload and save the file
    if not request.method == 'POST':
        return HttpResponse("must be POST")
    original_filename = request.POST.get('Filename')
    file = request.FILES.get('Filedata')
    print request.FILES
    print original_filename, file
    bucket, was_bucket_created = Bucket.objects.get_or_create(user=request.user)
    print bucket
    files = generic_handle_file(file, original_filename)
    for ifile, iname in files:
        iext = os.path.splitext(iname)[1].lower()
        print "extension: ", iext
        if iext in ['.jpg','.jpeg','.png','.gif']:
            imageform = UploadFileForm({'original_filename':iname,'owner': request.user.pk}, {'file':ifile})
            if imageform.is_valid():
                print 'imageform is valid'
                image = imageform.save(commit=False)
                image.save()
                bi = BucketItem(bucket=bucket, file=image)
                bi.save()
                print image
            else:
                print imageform.errors
    return HttpResponse("ok")

def empty_bucket_in_folder(request):
    if request.method=='POST':
        folder = Folder.objects.get( id=request.POST.get('folder_id') )
        bucket = Bucket.objects.get( id=request.POST.get('bucket_id') )
        tools.move_files_from_bucket_to_folder(bucket, folder)
        tools.empty_bucket(bucket)
    return HttpResponseRedirect( request.POST.get('redirect_to', '') )

def clone_bucket_to_folder(request):
    if request.method=='POST':
        folder = Folder.objects.get( id=request.POST.get('folder_id') )
        bucket = Bucket.objects.get( id=request.POST.get('bucket_id') )
        tools.move_files_from_bucket_to_folder(bucket, folder)
        tools.empty_bucket(bucket)
    return HttpResponseRedirect( request.POST.get('redirect_to', '') )

def empty_bucket(request):
    if request.method=='POST':
        bucket = Bucket.objects.get( id=request.POST.get('bucket_id') )
        tools.empty_bucket(bucket)
    return HttpResponseRedirect( request.POST.get('redirect_to', '') )

def put_file_in_bucket(request):
    if request.method=='POST':
        file_id = request.POST.get("file_id", None)
        bucket = tools.get_user_bucket(request.user)
        if file_id:
            file = Image.objects.get(id=file_id)
            tools.put_files_in_bucket([file], bucket)
    return HttpResponseRedirect( request.POST.get('redirect_to', '') )

def clone_files_from_bucket_to_folder(request):
    if request.method=='POST':
        bucket = Bucket.objects.get( id=request.POST.get('bucket_id') )
        folder = Folder.objects.get( id=request.POST.get('folder_id') )
        tools.clone_files_from_bucket_to_folder(bucket, folder)
    return HttpResponseRedirect( request.POST.get('redirect_to', '') )

class ImageExportForm(forms.Form):
    FORMAT_CHOICES = (
        ('jpg', 'jpg'),
        ('png', 'png'),
        ('gif', 'gif'),
        #('tif', 'tif'),
    )
    format = forms.ChoiceField(choices=FORMAT_CHOICES)
    
    crop = forms.BooleanField(required=False)
    upscale = forms.BooleanField(required=False)
    
    width = forms.IntegerField()
    height = forms.IntegerField()
    
    
import filters
def export_image(request, image_id):
    image = Image.objects.get(id=image_id)
    
    if request.method=='POST':
        form = ImageExportForm(request.POST)
        if form.is_valid():
            resize_filter = filters.ResizeFilter()
            im = filters.Image.open(image.file.path)
            format = form.cleaned_data['format']
            if format=='png':
                mimetype='image/jpg'
                pil_format = 'PNG'
            #elif format=='tif':
            #    mimetype='image/tiff'
            #    pil_format = 'TIFF'
            elif format=='gif':
                mimetype='image/gif'
                pil_format = 'GIF'
            else:
                mimetype='image/jpg'
                pil_format = 'JPEG'
            im = resize_filter.render(im,
                    size_x=int(form.cleaned_data['width']), 
                    size_y=int(form.cleaned_data['height']), 
                    crop=form.cleaned_data['crop'],
                    upscale=form.cleaned_data['upscale']
            )
            response = HttpResponse(mimetype='%s' % mimetype)
            response['Content-Disposition'] = 'attachment; filename=exported_image.%s' % format
            im.save(response, pil_format)
            return response
    else:
        form = ImageExportForm(initial={'crop': True, 'width': image.file.width, 'height':image.file.height})
    return render_to_response('image_filer/image_export_form.html', {
            'form': form,
            'image': image
    }, context_instance=RequestContext(request)) 

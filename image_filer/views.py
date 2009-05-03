import os
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden,HttpResponseBadRequest
from django.contrib.sessions.models import Session
from django.conf import settings
from django.db.models import Q

from models import Folder, Image, Clipboard, ClipboardItem
from models import tools
from models import FolderRoot, UnfiledImages, ImagesWithMissingData

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
    
@login_required
def directory_listing(request, folder_id=None, viewtype=None):
    clipboard = tools.get_user_clipboard(request.user)
    if viewtype=='images_with_missing_data':
        folder = ImagesWithMissingData()
    elif viewtype=='unfiled_images':
        folder = UnfiledImages()
    elif folder_id == None:
        folder = FolderRoot()
    else:
        folder = Folder.objects.get(id=folder_id)
        
    # search
    def filter_folder(qs, terms=[]):
        for term in terms:
            qs = qs.filter(Q(name__icontains=term) | Q(owner__username__icontains=term) | Q(owner__first_name__icontains=term) | Q(owner__last_name__icontains=term)  )  
        return qs
    def filter_image(qs, terms=[]):
        for term in terms:
            qs = qs.filter( Q(name__icontains=term) | Q(original_filename__icontains=term ) | Q(owner__username__icontains=term) | Q(owner__first_name__icontains=term) | Q(owner__last_name__icontains=term) )
        return qs
    q = request.GET.get('q', None)
    if q:
        search_terms = q.split(" ")
    else:
        search_terms = []
    limit_search_to_folder = request.GET.get('limit_search_to_folder', False) in (True, 'on')

    if len(search_terms)>0:
        if folder and limit_search_to_folder and not folder.is_root:
            folder_qs = folder.get_descendants()
            # TODO: check how folder__in=folder.get_descendats() performs in large trees
            image_qs = Image.objects.filter(folder__in=folder.get_descendants())
        else:
            folder_qs = Folder.objects.all()
            image_qs = Image.objects.all()
        folder_qs = filter_folder(folder_qs, search_terms)
        image_qs = filter_image(image_qs, search_terms)
            
        show_result_count = True
    else:
        folder_qs = folder.children.all()
        image_qs = folder.image_files.all()
        show_result_count = False
    
    folder_qs = folder_qs.order_by('name')
    image_qs = image_qs.order_by('name')
    
    folder_children = []
    folder_files = []
    for f in folder_qs:
        f.perms = _userperms(f, request)
        if hasattr(f, 'has_read_permission'):
            if f.has_read_permission(request):
                folder_children.append(f)
        else:
            folder_children.append(f) 
    for f in image_qs:
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
    return render_to_response('image_filer/directory_listing.html', {
            'folder':folder,
            'folder_children':folder_children,
            'folder_files':folder_files,
            'permissions': permissions,
            'permstest': _userperms(folder, request),
            'current_url': request.path,
            'title': u'Directory listing for %s' % folder.name,
            'search_string': ' '.join(search_terms),
            'show_result_count': show_result_count,
            'limit_search_to_folder': limit_search_to_folder,
        }, context_instance=RequestContext(request))

@login_required
def edit_folder(request, folder_id):
    # TODO: implement edit_folder view
    folder=None
    return render_to_response('image_filer/folder_edit.html', {
            'folder':folder,
        }, context_instance=RequestContext(request))

@login_required
def edit_image(request, folder_id):
    # TODO: implement edit_image view
    folder=None
    return render_to_response('image_filer/image_edit.html', {
            'folder':folder,
        }, context_instance=RequestContext(request))

@login_required
def make_folder(request, folder_id=None):
    if not folder_id:
        folder_id = request.REQUEST.get('parent_id', None)
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
            print u"Saving folder %s as child of %s" % (new_folder, folder)
            return HttpResponse('<script type="text/javascript">opener.dismissPopupAndReload(window);</script>')
    else:
        print u"New Folder GET, parent %s" % folder
        new_folder_form = NewFolderForm()
    return render_to_response('image_filer/include/new_folder_form.html', {
            'new_folder_form': new_folder_form,
            'is_popup': request.REQUEST.has_key('_popup'),
    }, context_instance=RequestContext(request))

class UploadFileForm(forms.ModelForm):
    class Meta:
        model=Image
        #fields = ('file',)
        
from image_filer.utils.files import generic_handle_file

@login_required
def upload(request):
    return render_to_response('image_filer/upload.html', {
                    'is_popup': request.REQUEST.has_key('_popup'),
                    'title': u'Upload files',
                    }, context_instance=RequestContext(request))

def ajax_upload(request, folder_id=None):
    """
    receives an upload from the flash uploader and fixes the session
    because of the missing cookie. Receives only one file at the time, 
    althow it may be a zip file, that will be unpacked.
    """
    print request.POST
    # flashcookie-hack (flash does not submit the cookie, so we send the
    # django sessionid over regular post
    engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
    #session_key = request.POST.get('jsessionid')
    # this sucks... session key in get!
    session_key = request.GET.get('jsessionid')
    request.session = engine.SessionStore(session_key)
    print request.session.session_key, request.user
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
    #print request.FILES
    #print original_filename, file
    clipboard, was_bucket_created = Clipboard.objects.get_or_create(user=request.user)
    files = generic_handle_file(file, original_filename)
    for ifile, iname in files:
        iext = os.path.splitext(iname)[1].lower()
        #print "extension: ", iext
        if iext in ['.jpg','.jpeg','.png','.gif']:
            imageform = UploadFileForm({'original_filename':iname,'owner': request.user.pk}, {'file':ifile})
            if imageform.is_valid():
                print 'imageform is valid'
                image = imageform.save(commit=False)
                image.save()
                bi = ClipboardItem(clipboard=clipboard, file=image)
                bi.save()
                print image
            else:
                pass#print imageform.errors
    return HttpResponse("ok")

@login_required
def paste_clipboard_to_folder(request):
    if request.method=='POST':
        folder = Folder.objects.get( id=request.POST.get('folder_id') )
        print folder
        clipboard = Clipboard.objects.get( id=request.POST.get('clipboard_id') )
        tools.move_files_from_clipboard_to_folder(clipboard, folder)
        tools.discard_clipboard(clipboard)
    return HttpResponseRedirect( request.POST.get('redirect_to', '') )

@login_required
def clone_clipboard_to_folder(request):
    if request.method=='POST':
        folder = Folder.objects.get( id=request.POST.get('folder_id') )
        clipboard = Clipboard.objects.get( id=request.POST.get('clipboard_id') )
        tools.move_files_from_clipboard_to_folder(clipboard, folder)
        tools.discard_clipboard(clipboard)
    return HttpResponseRedirect( request.POST.get('redirect_to', '') )

@login_required
def discard_clipboard(request):
    if request.method=='POST':
        clipboard = Clipboard.objects.get( id=request.POST.get('clipboard_id') )
        tools.discard_clipboard(clipboard)
    return HttpResponseRedirect( request.POST.get('redirect_to', '') )

@login_required
def delete_clipboard(request):
    if request.method=='POST':
        clipboard = Clipboard.objects.get( id=request.POST.get('clipboard_id') )
        tools.delete_clipboard(clipboard)
    return HttpResponseRedirect( request.POST.get('redirect_to', '') )


@login_required
def move_file_to_clipboard(request):
    if request.method=='POST':
        file_id = request.POST.get("file_id", None)
        clipboard = tools.get_user_clipboard(request.user)
        if file_id:
            file = Image.objects.get(id=file_id)
            tools.move_file_to_clipboard([file], clipboard)
    return HttpResponseRedirect( request.POST.get('redirect_to', '') )

@login_required
def clone_files_from_clipboard_to_folder(request):
    if request.method=='POST':
        clipboard = Clipboard.objects.get( id=request.POST.get('clipboard_id') )
        folder = Folder.objects.get( id=request.POST.get('folder_id') )
        tools.clone_files_from_clipboard_to_folder(clipboard, folder)
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
@login_required
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

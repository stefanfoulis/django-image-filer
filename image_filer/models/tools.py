from image_filer.models import Bucket


def empty_bucket(bucket):
    bucket.files.clear()

def get_user_bucket(user):
    if user.is_authenticated():
        bucket, was_bucket_created = Bucket.objects.get_or_create(user=user)
        return bucket

def put_files_in_bucket(files, bucket):
    for file in files:
        bucket.append_file(file)
    return True
def clone_files_from_bucket_to_folder(bucket, folder):
    for file in bucket.files.all():
        cloned_file = file.clone()
        cloned_file.folder = folder
        cloned_file.save()

def move_files_from_bucket_to_folder(bucket, folder):
    return move_files_to_folder(bucket.files.all(), folder)

def move_files_to_folder(files, folder):
    for file in files:
        file.folder = folder
        file.save()
    return True
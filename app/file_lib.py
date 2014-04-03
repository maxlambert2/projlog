from PIL import Image
import cStringIO
import config
import uuid

def get_s3_url(object_name):
    return 'https://s3.amazonaws.com/%s/%s' % (config.AWS_S3_BUCKET, object_name)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def resize_image(filepath, width=config.PROFILE_PIC_WIDTH):
    image = Image.open(filepath)

    #(width, height) = image.size
    new_width = width
    new_height = width

    resizedImage = image.resize((new_width, new_height))

    # Turn back into file-like object
    resizedImageFile = cStringIO.StringIO()
    resizedImage.save(resizedImageFile , 'PNG', optimize = True)
    resizedImageFile.seek(0)    # So that the next read starts at the beginning

    return resizedImageFile
    
def generate_filename(seed='z',ext=config.DEFAULT_IMG_EXT):
    return seed+'-'+str(uuid.uuid4())+ext
    
def get_crop_size_by_scaleup(cls, input_dimension, scale_dimension):
    """
    From the original dimension, a target dimension is given
    Before resizing, the original image should be cropped based on the 
    best scale dimension.
    """
    # If somehow, scale dimension is larger than the original size,
    # don't scale and return the original instead
    new_size = input_dimension
    if input_dimension[0] >= scale_dimension[0] or input_dimension[1] >= scale_dimension[1]:
        by_width = cls.get_size_by_width(scale_dimension, input_dimension)
        by_height = cls.get_size_by_height(scale_dimension, input_dimension)
        if by_width[0] <= input_dimension[0] and by_width[1] <= input_dimension[1]:
            new_size = by_width
        else:
            new_size = by_height
    return new_size
 

def get_size_by_width(cls, input_dimension, scale_dimension):
    width = scale_dimension[0]
    # Get the height based on scaled image dimension against base width
    width_percent = (width / float(input_dimension[0]))
    height = int((float(input_dimension[1]) * float(width_percent)))
    return (width, height)
 

def get_size_by_height(cls, input_dimension, scale_dimension):
    height = scale_dimension[1]
    # Get the width based on scaled image dimension against base height
    height_percent = (height / float(input_dimension[1]))
    width = int((float(input_dimension[0]) * float(height_percent)))
    return (width, height)
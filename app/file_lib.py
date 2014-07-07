from PIL import Image
import cStringIO
import config
import uuid
from math import floor

def get_s3_url(object_name, folder=None):
    if object_name is None or object_name == '':
        return None
    if folder is None or folder == '':
        return 'https://s3.amazonaws.com/%s/%s' % (config.AWS_S3_BUCKET, object_name)
    else:
        return 'https://s3.amazonaws.com/%s/%s/%s' % (config.AWS_S3_BUCKET, folder, object_name)
        

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS
           
# def upload_to_s3(bucket, file, filename):
#     k = Key(bucket)
#     k.key = 

def resize_and_crop(img_path, size, crop_type='top'):
    """
    Resize and crop an image to fit the specified size.
 
    args:
        img_path: path for the image to resize.
        modified_path: path to store the modified image.
        size: `(width, height)` tuple.
        crop_type: can be 'top', 'middle' or 'bottom', depending on this
            value, the image will cropped getting the 'top/left', 'midle' or
            'bottom/rigth' of the image to fit the size.
    raises:
        Exception: if can not open the file in img_path of there is problems
            to save the image.
        ValueError: if an invalid `crop_type` is provided.
    """
    # If height is higher we resize vertically, if not we resize horizontally
    img = Image.open(img_path)
    # Get current and desired ratio for the images
    img_ratio = img.size[0] / float(img.size[1])
    ratio = size[0] / float(size[1])
    #The image is scaled/cropped vertically or horizontally depending on the ratio
    if ratio > img_ratio:
        img = img.resize((size[0], size[0] * img.size[1] / img.size[0]),
                Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, img.size[0], size[1])
        elif crop_type == 'middle':
            box = (0, (img.size[1] - size[1]) / 2, img.size[0], (img.size[1] + size[1]) / 2)
        elif crop_type == 'bottom':
            box = (0, img.size[1] - size[1], img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    elif ratio < img_ratio:
        img = img.resize((size[1] * img.size[0] / img.size[1], size[1]),
                Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, size[0], img.size[1])
        elif crop_type == 'middle':
            box = ((img.size[0] - size[0]) / 2, 0, (img.size[0] + size[0]) / 2, img.size[1])
        elif crop_type == 'bottom':
            box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    else :
        img = img.resize((size[0], size[1]),
                Image.ANTIALIAS)
    
    resizedImage=img
    # Turn back into file-like object
    resizedImageFile = cStringIO.StringIO()
    resizedImage.save(resizedImageFile , config.DEFAULT_IMG_EXT, optimize = True)
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
from collections import OrderedDict

import keras

from ..utils._config_template import ConfigTemplate
from ..utils._validation import (
    is_valid_img_shape,
    is_valid_input_tensor
)

from .backbone import load_backbone_pyramid_feautre_shapes_fn


class RetinaNetConfig(ConfigTemplate):
    """ For help on RetinaNetConfig, use RetinaNetConfig(help=True) """

    def __init__(self, help=False, **kwargs):
        self.__name__ = 'RetinaNetConfig'
        self.__params__ = OrderedDict()

        # Params most people will look for first

        self.add(
            'name',
            'Name of your model',
            default = 'retinanet',
            accepted_types = str
        )

        self.add(
            'num_classes',
            'Number of classes',
            required = True,
            accepted_types = 'int-like'
        )

        self.add(
            'input_shape',
            'Shape of your input',
            condition = is_valid_img_shape
        )

        self.add(
            'input_tensor',
            'Tensor as an input (overwrites input_shape)',
            condition = is_valid_input_tensor
        )

        # Loss and optimizer config

        self.add(
            'classification_loss_options',
            'Kwarg inputs for classification loss (focal loss) in dict form',
            default = {}
        )

        self.add(
            'regression_loss_options',
            'Kwarg inputs for regression loss (smooth l1 loss) in dict form',
            default = {}
        )

        self.add(
            'optimizer_name',
            'The name of a keras available optimizer from https://keras.io/optimizers/, default adam',
            default = 'adam'
        )

        self.add(
            'optimizer_options',
            'Kwarg inputs for optimizers (in dict form), common inputs are lr, clipnorm, clipvalue, decay',
            default = {
                'lr': 1e-5,
                'clipnorm': 0.001
            }
        )

        # Backbone config

        self.add(
            'backbone_name',
            'Loads a backbone based on a valid name',
            default = 'resnet50',
            valid_options = ['inception_v3', 'resnet50', 'vgg16']
        )

        self.add(
            'freeze_backbone',
            'Freezes the backbone weights during training',
            default = False,
            accepted_types = bool
        )

        # Model config

        self.add(
            'pyramid_feature_size',
            'Number of features at the pyramid level',
            default = 256,
            accepted_types = 'int-like'
        )

        self.add(
            'classification_feature_size',
            'Number of features used in classification layers',
            default = 256,
            accepted_types = 'int-like'
        )

        self.add(
            'regression_feature_size',
            'Number of features used in anchor regression layers',
            default = 256,
            accepted_types = 'int-like'
        )

        self.add(
            'anchor_sizes',
            'List of size of anchor',
            default = [32, 64, 128, 256, 512],
            accepted_types = 'list-like'
        )

        self.add(
            'anchor_strides',
            'List of strides of anchor (needs to be the same length)',
            default = [8, 16, 32, 64, 128],
            accepted_types = 'list-like'
        )

        self.add(
            'anchor_ratios',
            'List of ratios that anchor are generated wrt a window',
            default = [0.5, 1., 2.],
            accepted_types = 'list-like'
        )

        self.add(
            'anchor_scales',
            'List of scales that anchor are generated wrt a window',
            default = [2. ** 0., 2. ** (1. / 3.), 2. ** (2. / 3.)],
            accepted_types = 'list-like'
        )


        if help:
            self.help()
        else:
            self._validate_kwargs_(**kwargs)


    def _validate_kwargs_(self, **kwargs):
        super(RetinaNetConfig, self)._validate_kwargs_(**kwargs)

        # Anchor strides and sizes must be the same size
        assert len(self.anchor_sizes) == len(self.anchor_strides)

        # Assign proper input_shape and input_tensor
        if self.input_tensor is None:
            if self.input_shape is None:
                self.input_shape  = (None, None, 3)
                self.input_tensor = keras.Input(shape=(None, None, 3))
            else:
                self.input_tensor = keras.Input(shape=self.input_shape)
        else:
            self.input_shape = tuple(self.input_tensor.shape[1:].as_list())

        # Load compute_pyramid_feature_shapes_for_img_shape function
        self.compute_pyramid_feature_shapes_for_img_shape = \
            load_backbone_pyramid_feautre_shapes_fn(self.backbone_name)


    def get_num_anchors(self):
        return len(self.anchor_ratios) * len(self.anchor_scales)

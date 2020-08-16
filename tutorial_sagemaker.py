# SAGEMAKER - 3d-photo-inpainting endpoint
# https://github.com/vt-vl-lab/3d-photo-inpainting
# https://medium.com/@samuelabiodun/how-to-deploy-a-pytorch-model-on-sagemaker-aa9a38a277b6
# https://github.com/abiodunjames/MachineLearning/tree/master/DeployYourModelToSageMaker

# TODO 
# 1.
# - download model using: https://github.com/vt-vl-lab/3d-photo-inpainting/blob/master/download.sh
# wget https://filebox.ece.vt.edu/~jbhuang/project/3DPhoto/model/color-model.pth
# wget https://filebox.ece.vt.edu/~jbhuang/project/3DPhoto/model/depth-model.pth
# wget https://filebox.ece.vt.edu/~jbhuang/project/3DPhoto/model/edge-model.pth
# wget https://filebox.ece.vt.edu/~jbhuang/project/3DPhoto/model/model.pt
#
# 2.
# - create S3 bucket and upload model(s)
#
# 3.
# - In inference.py, specify how the SageMaker model server should load and serve the model:
# MUST implement 3 functions: input_fn, predict_fn, output_fn
#
# 4.
# - create Jupyter notebook in same directory as inference.py
# EXAMPLE deploy.ipynb:

#filename deploy.ipynb
from sagemaker.pytorch import PyTorchModel
from sagemaker import get_execution_role
role = get_execution_role()

# You can also configure a sagemaker role and reference it by its name.
# role = "CustomSageMakerRoleName"
# pytorch_model = PyTorchModel(model_data='s3://pytorch-sagemaker-example/model.tar.gz', role=role, entry_point='inference.py', framework_version='1.3.1')
pytorch_model = PyTorchModel(model_data='s3://sjcobb_bucket/3DPhoto/model.tar.gz', role=role, entry_point='inference.py', framework_version='1.3.1')

predictor = pytorch_model.deploy(instance_type='ml.t2.medium', initial_instance_count=1)

#
#
# 5.
# - In SageMaker, open Jupyter notebook instance, there should be two files (inference.py & deploy.ipynb). 
# - Open and execute deploy.ipynb by choosing 'Run All' from the cell menu. This will deploy the model, as well as the endpoint.
# - On successful deployment, you can make real-time predictions using InvokeEndpoint by sending a JSON object with a url of image to predict. For example: {"url":"https://example.com/predict.png"}
# - https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_runtime_InvokeEndpoint.html
#
#
# 6 - a.
# - Create new application in github.com/sjcobb with call to InvokeEndpoint
# - requests are authenticated using AWS Signature Version 4: https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-authenticating-requests.html
# - POST request should use HTTP Authorization header: https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-auth-using-authorization-header.html
# - EXAMPLE InvokeEndpoint Syntax:

POST /endpoints/EndpointName/invocations HTTP/1.1
Content-Type: ContentType
Accept: Accept
X-Amzn-SageMaker-Custom-Attributes: CustomAttributes
X-Amzn-SageMaker-Target-Model: TargetModel
X-Amzn-SageMaker-Target-Variant: TargetVariant

Body # common request body formats: https://docs.aws.amazon.com/sagemaker/latest/dg/cdf-inference.html

# 6 - b.
# - endpoint can also be invoked through a lambda function, see ex: https://gist.github.com/abiodunjames/023451c87a3da05688caaacb2b754457
# - make sure your lambda function has invoke permission
# - 
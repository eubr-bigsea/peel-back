from flask_restx import Resource, Namespace
from logger import setup_logger
from werkzeug.datastructures import FileStorage
from enum import Enum
from werkzeug.utils import secure_filename
import os
import re

# file type enum for request validation and swagger documentation
class FileType(str, Enum):
    model = 'model'
    datasource = 'datasource'

# folders and allowed extensions for each FileType
UPLOAD_FOLDERS = {'datasource':'storage/data', 'model':'storage/models'}
ALLOWED_EXTENSIONS = {'datasource':['csv'], 'model':['pkl']}

def allowed_file(filename, fileType):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS[fileType]

def rename_file(filename):
    # padrao para pegar arquivos terminados em "_dup(QUALQUER NUMERO)", dup se refere a duplicado
    pattern = r".*_dup\d+$"
    filename = filename.split('.')
    rawname = filename[-2]
    if re.match(pattern, rawname):
        rawname = rawname.split('_')
        rawname[-1] = 'dup'+str(int(rawname[-1].replace('dup',''))+1)
        rawname = '_'.join(rawname)
    else:
        rawname = rawname + '_dup1'
    filename[-2] = rawname
    return '.'.join(filename)

ns = Namespace('Uploader', description='Upload de modelos/fontes de dados')

parser = ns.parser()
parser.add_argument('type', type=FileType, help='Tipo de arquivo para upload', 
                    choices=list(FileType), location='args', required=True)

parser.add_argument('file', type=FileStorage, location='files',
                    help='Arquivo para upload', required=True)


logger = setup_logger()

@ns.route('/')
class Uploader(Resource):
    @ns.expect(parser, validate=True)
    def post(self):
        """
        Upload de qualquer arquivo CSV e PKL para datasources e mdoelos
        Verifica strings e salva arquivos dependendo do parâmetro de URL para FileType, também verifica se nome do arquivo que está sendo salvo é seguro.
        """
        try:
            args = parser.parse_args()
            file = args['file'] 
            fileType = args['type']

            if file.filename == '':
               raise FileNotFoundError("Nenhum arquivo foi enviado utilizando o parâmetro 'file'")

            if file and allowed_file(file.filename, fileType):
                filename = secure_filename(file.filename)
                uri = os.path.join(UPLOAD_FOLDERS[fileType],filename)

                while os.path.exists(uri):
                    filename = rename_file(filename)
                    uri = os.path.join(UPLOAD_FOLDERS[fileType],filename)
                    
                file.save(uri)
                return {'status': 'UPLOADED', 'filename': filename, 'uri': uri}, 201
            else:
                raise TypeError(f'A extensão utilizada não é permitida para o tipo de arquivo {fileType}. São permitidas as seguintes: {ALLOWED_EXTENSIONS[fileType]}')
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Um erro ocorreu: {e}")
            return {"error": f"[{self.__class__.__name__}] Um erro ocorreu ao processar a requisição.", "message": str(e)}, 500
from flask_restx import Api

api = Api(
    title='Peel XAI API',
    version='0.1',
    description='Peel API for eXplainable Artificial Intelligence (XAI) '
                'with tools like SHAP, LIME, Captum, and GPX, providing '
                'detailed explanations for end-users.',
    contact='Leonardo Augusto Ferreira',
    contact_email='leauferreira@gmail.com',
)

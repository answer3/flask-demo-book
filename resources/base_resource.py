from flask_restful import Resource, reqparse


class BaseResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('page', type=int, location='args', required=False, default=1, help='Page number')
        self.reqparse.add_argument('per_page', type=int, location='args', required=False, default=10, help='Items per page')
        self.reqparse.add_argument('q', type=str, location='args', required=False, default=None,
                                   help='Search query')
        super(BaseResource, self).__init__()

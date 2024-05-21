from flask import abort


def get_entity_or_404(db_session, model, id):
    entity = db_session.get(model, id)
    if not entity:
        return abort(404, description="Entity {} doesn't exist".format(id))
    return entity

def xml_over_json(request):
    accepted = request.accept_mimetypes.best_match(['application/xml', 'text/xml', 'application/json'])
    return accepted == 'application/xml' or accepted == 'text/xml'

def json_over_xml(request):
    accepted = request.accept_mimetypes.best_match(['application/xml', 'text/xml', 'application/json'])
    return accepted == 'application/json'
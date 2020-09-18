import kopf
import kubernetes


@kopf.on.create('muge.net', 'v1', 'databases')
def create_fn(body,spec, meta, status, **kwargs):
    # Get info from Database object
    name = body['metadata']['name']
    namespace = body['metadata']['namespace']
    db_type = spec['type']
    tag = spec['tag'] if spec['tag'] else 'latest'

    # Make sure type is provided
    if not db_type:
        raise kopf.HandlerFatalError(f'Type must be set. Got {db_type}.')

    # Pod template
    pod = {'apiVersion': 'v1', 'metadata': {'name': name, 'labels': {'app': 'db'}}}

    # Service template
    svc = {'apiVersion': 'v1', 'metadata': {'name': name},'spec': {'selector': {'app': 'db'}, 'type': 'NodePort'}}

    # Update templates based on Database specification
    image = f'{db_type}:{tag}'
    pod['spec'] = {'containers': [{'image': image, 'name': db_type}]}
    if db_type == 'mongo':
        port = 27017
    if db_type == 'mysql':
        port = 3306
        pod['spec']['containers'][0]['env'] = [{'name': 'MYSQL_ROOT_PASSWORD', 'value': 'my_passwd'}]
    svc['spec']['ports'] = [{'port': port, 'targetPort': port}]

    # Make the Pod and Service the children of the Database object
    kopf.adopt(pod, owner=body)
    kopf.adopt(svc, owner=body)

    # Object used to communicate with the API Server
    api = kubernetes.client.CoreV1Api()

    # Create Pod
    obj = api.create_namespaced_pod(namespace, pod)
    print(f"Pod {obj.metadata.name} created")

    # Create Service
    obj = api.create_namespaced_service(namespace, svc)
    print(f"NodePort Service {obj.metadata.name} created, exposing on port {obj.spec.ports[0].node_port}")

    # Update status
    msg = f"Pod and Service created by Database {name}"
    return {'message': msg}


@kopf.on.delete('muge.net', 'v1', 'databases')
def delete(body, **kwargs):
    msg = f"Database {body['metadata']['name']} and its Pod / Service children deleted"
    return {'message': msg}

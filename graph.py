from arango_db import *
from vk_api_for_graph import *


class Graph:
    def __init__(self, db_name, graph_name):
        self.db = ArangoDb(db_name).db
        self.graph = self.find_or_create_graph(graph_name)

    def find_or_create_graph(self, graph_name):
        if self.db.has_graph(graph_name):
            return self.db.graph(graph_name)
        else:
            return self.db.create_graph(graph_name)

    def find_or_create_vertex_collection(self, collection_name):
        if self.graph.has_vertex_collection(collection_name):
            return self.graph.vertex_collection(collection_name)
        else:
            return self.graph.create_vertex_collection(collection_name)

    def find_or_create_edge_definition(self, definition_name,
                                       vertex_collection_name):
        if self.graph.has_edge_definition(definition_name):
            return self.graph.edge_collection(definition_name)
        else:
            return self.graph.create_edge_definition(
                edge_collection=definition_name,
                from_vertex_collections=[vertex_collection_name],
                to_vertex_collections=[vertex_collection_name]
            )


graph = Graph('social_graph_db', 'vk')
users = graph.find_or_create_vertex_collection('users')
friends = graph.find_or_create_edge_definition('friends', 'users')
vkontakte_api = VkApiForGraph()


def bfs(start_vk_id, goal_vk_id, stop_level=6):
    start_vk_id = int(start_vk_id)
    goal_vk_id = int(goal_vk_id)
    level = 0
    stop_condition = False
    queue = [[None, start_vk_id, level]]
    insert_user(start_vk_id)

    while queue:
        current = queue.pop(0)
        print(f'Текущий: {current}')
        id = current[1]
        parent = current[0]
        level = current[2] + 1
        if level > stop_level:
            break
        insert_user(id)
        if parent:
            insert_friend(parent, id)

        if id == goal_vk_id:
            return True

        if not stop_condition:
            friends_list = vkontakte_api.get_friends(id)
            stop_condition = goal_vk_id in friends_list
            if stop_condition:
                queue = [[id, goal_vk_id, level]]
            else:
                ids_in_queue = [elem[1] for elem in queue]
                queue.extend(
                    [[id, friend, level] for friend in friends_list
                        if friend not in ids_in_queue]
                )

        print(f'Очередь: {len(queue)}')
        print('')

    return False


def insert_user(vk_id):
    if not users.has(str(vk_id)):
        users.insert({'_key': str(vk_id)})


def insert_friend(first_vk_id, last_vk_id):
    if not (friends.has(f'{first_vk_id}-{last_vk_id}') or
            friends.has(f'{last_vk_id}-{first_vk_id}')):
        friends.insert({
            '_key': f'{first_vk_id}-{last_vk_id}',
            '_from': f'users/{first_vk_id}',
            '_to': f'users/{last_vk_id}'
        })


def find_path(start_vk_id, target_vk_id):
    cursor = graph.db.aql.execute(
        'FOR v, e '
        'IN OUTBOUND SHORTEST_PATH '
        "@start_vertex TO @target_vertex "
        "GRAPH 'vk' "
        'RETURN v._key',
        bind_vars={'start_vertex': f'users/{start_vk_id}',
                   'target_vertex': f'users/{target_vk_id}'}
    )
    result = [doc for doc in cursor]

    return result

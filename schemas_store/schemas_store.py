# -*- coding: utf-8 -*-
import os
import json
from re import compile

from jsonschema import Draft4Validator

from ._tree import Tree


VERSION_RE = compile(r'schema_(?P<version>\d+).json')
INDEX_RE = compile(r'/(?P<index>\d+)$')


class SchemaStore(object):
    """  Object that work with schemas """

    root = None

    def __init__(self):
        """ Init path and update schema(IO operation) """
        self.path = os.getcwd()
        self.update_schemas_id(self.path + '/schemas_store/schemas')

    def load(self):
        """ Create root """
        self.root = Tree()
        self.build_tree(self.root, self.path + '/schemas_store/schemas')

    def find(self, code, version='latest'):
        """
        Get schema by code
        :param code: str
        :param version: str example "001"
        :return: schema or None
        """
        pass

    def build_tree(self, tree, path):
        """
        Build tree from schemas
        :param tree: _tree.Tree
        :param path: os.path
        """
        # import pdb; pdb.set_trace()
        for elem_name in os.listdir(path):
            if elem_name.endswith('.json'):
                with open(os.path.join(path, elem_name)) as f:
                    schema_json = json.load(f)
                    reg_group = VERSION_RE.search(elem_name).groupdict()
                    tree.versions[reg_group['version']] = Draft4Validator(schema_json)
            else:
                if os.path.isdir(os.path.join(path, elem_name)):
                    child = Tree(index=elem_name)
                    tree.children.append(child)
                    self.build_tree(child, os.path.join(path, elem_name))

    def _go_by_schema(self, path, handler_file, handler_path):
        """
        Go by direcotory and call handler_file and find json and
        call handler path when find another directory
        :param path: os.path
        :param handler_file: function which call when find file
        :param handler_path: function which call when find directory
        :return: None
        """
        for elem_name in os.listdir(path):
            if elem_name.endswith('.json'):
                handler_file(os.path.join(path, elem_name))
            else:
                if os.path.isdir(path+'/'+elem_name):
                    handler_path(path+'/'+elem_name,
                                 self.update_file,
                                 self._go_by_schema)

    def update_schemas_id(self, path):
        """
        Update every schemas id
        :param path: os.path
        """
        self._go_by_schema(path, self.update_file, self._go_by_schema)

    def update_file(self, file_path):
        """
        Update schema id
        :param file_path: os.path
        """
        with open(file_path, 'r+') as f:
            schema_json = json.load(f)
            schema_json['id'] = "file://{package}/schemas_store/schemas{schema}".format(
                package=self.path,
                schema=schema_json['id'].split('schemas')[-1])
            f.seek(0)
            f.truncate()
            json.dump(schema_json,
                      f,
                      indent=4,
                      separators=(',', ': '),
                      ensure_ascii=False)

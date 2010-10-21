from DataFactory import dbPages
from DataFactory import dbPageModules

def build_tree(nodes, **kwargs):
    # create empty tree to fill
    t = {}
    pageTree = {}
    # Main View is for tree show on main page not edit mode
    pageModules = False
    if 'pageModules' in kwargs:
        pageModules = kwargs['pageModules']
        
    # First group all pages w/ same parent
    for node in nodes:
        # Where parentKey is None, this tells us that node is a root level node
        if node.parentKey is None:
            key = 'root'
        else:
            key = node.parentKey.key()
            
        if not t.has_key(key):
            t[key] = []
            
        # If pagemodules are present, we need to store them along side the page object
        # to display proper menu and paths i main view
        if pageModules:
            # TODO: Shouldn't need to loop for every node
            for pageModule in pageModules:
                if pageModule.pageKey.key() == node.key():
                    t[key].append({ 'page' : node, 'pageModule' : pageModule, 'children' : []})
        else:
            t[key].append({ 'page' : node, 'children' : []})
    
    if 'pageRoot' in kwargs:
        pageRoot = kwargs['pageRoot']
        pageTree = [{ 'page' : pageRoot, 'children' : []}]
    else:
        if t.has_key('root'):
            pageTree = t['root']
    # Iterate over there
    
    build_page_tree(pageTree, t)
        
    return pageTree

def build_page_tree(pageTree, nodes):
    #Loop over selected list
    for parent, node in nodes.iteritems():
        # We don't need to loop over the root level node
        if parent is not 'root':
            # Loop over current level in page tree
            for item in pageTree:
                # Match keys
                if item['page'].key() == parent:
                    # Save node as child
                    item['children'] = node
                    # Only need to loop over childs if they are present
                    build_page_tree(item['children'], nodes)
                
                
#def build_page_container_tree(nodes, pageConatiner, *args):
#    # create empty tree to fill
#    tree = {}
#    # fill in tree starting with roots (those with no parent)
#    build_tree_recursive(tree, pageConatiner.key(), nodes, *args)
#    
#    return tree
#
#def build_tree_recursive(tree, parent, nodes, *args):
#    # find root children, first level nodes have no parentKey
#    if parent is None:
#        children  = [n for n in nodes if n.parentKey == None]
#    # find children
#    else:
#        children  = [n for n in nodes if n.parentKey is not None and n.parentKey.key() == parent]
#    
#    # build a subtree for each child
#    for child in children:
#        # start new subtree
#        if not args:
#            key = child.key()
#            # Use page entry key as unique dict key
#            tree[key] = { 'page' : child, 'children' : {}}
#            # call recursively to build a subtree for current node
#            build_tree_recursive(tree[key]['children'], key, nodes)
#        else:
#            lang = args[0]
#            published = args[1]
#            key = child.key()
#            
#            pageModule = dbPageModules.PageModules.gql('WHERE pageKey = :pageKey AND lang = :lang AND published = :published', pageKey = key, lang = lang, published = published).get()
#            
#            if pageModule:
#                tree[key] = { 'name' : pageModule.name, 'path': pageModule.path, 'children' : {}}
#                # call recursively to build a subtree for current node
#                build_tree_recursive(tree[key]['children'], key, nodes, *args)
            
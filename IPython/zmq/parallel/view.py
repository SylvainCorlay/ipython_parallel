#!/usr/bin/env python
"""Views"""

from IPython.external.decorator import decorator


@decorator
def myblock(f, self, *args, **kwargs):
    block = self.client.block
    self.client.block = self.block
    ret = f(self, *args, **kwargs)
    self.client.block = block
    return ret

class View(object):
    """Base View class"""
    _targets = None
    block=None
    
    def __init__(self, client, targets):
        self.client = client
        self._targets = targets
        self.block = client.block
    
    def __repr__(self):
        strtargets = str(self._targets)
        if len(strtargets) > 16:
            strtargets = strtargets[:12]+'...]'
        return "<%s %s>"%(self.__class__.__name__, strtargets)
    
    @property
    def results(self):
        return self.client.results
    
    @property
    def targets(self):
        return self._targets
    
    @targets.setter
    def targets(self, value):
        raise TypeError("Cannot set my targets argument after construction!")
    
    def apply(self, f, *args, **kwargs):
        """calls f(*args, **kwargs) on remote engines, returning the result.
        
        This method does not involve the engine's namespace.
        
        if self.block is False:
            returns msg_id
        else:
            returns actual result of f(*args, **kwargs)
        """
        return self.client.apply(f, args, kwargs, block=self.block, targets=self.targets, bound=False)
    
    def apply_async(self, f, *args, **kwargs):
        """calls f(*args, **kwargs) on remote engines in a nonblocking manner.
        
        This method does not involve the engine's namespace.
        
        returns msg_id
        """
        return self.client.apply(f,args,kwargs, block=False, targets=self.targets, bound=False)
    
    def apply_sync(self, f, *args, **kwargs):
        """calls f(*args, **kwargs) on remote engines in a blocking manner,
         returning the result.
        
        This method does not involve the engine's namespace.
        
        returns: actual result of f(*args, **kwargs)
        """
        return self.client.apply(f,args,kwargs, block=True, targets=self.targets, bound=False)
    
    def apply_bound(self, f, *args, **kwargs):
        """calls f(*args, **kwargs) bound to engine namespace(s).
        
        if self.block is False:
            returns msg_id
        else:
            returns actual result of f(*args, **kwargs)
        
        This method has access to the targets' globals
        
        """
        return self.client.apply(f, args, kwargs, block=self.block, targets=self.targets, bound=True)
    
    def apply_async_bound(self, f, *args, **kwargs):
        """calls f(*args, **kwargs) bound to engine namespace(s) 
        in a nonblocking manner.
        
        returns: msg_id
        
        This method has access to the targets' globals
        
        """
        return self.client.apply(f, args, kwargs, block=False, targets=self.targets, bound=True)
    
    def apply_sync_bound(self, f, *args, **kwargs):
        """calls f(*args, **kwargs) bound to engine namespace(s), waiting for the result.
        
        returns: actual result of f(*args, **kwargs)
        
        This method has access to the targets' globals
        
        """
        return self.client.apply(f, args, kwargs, block=False, targets=self.targets, bound=True)
    

class DirectView(View):
    """Direct Multiplexer View"""
    
    def update(self, ns):
        """update remote namespace with dict `ns`"""
        return self.client.push(ns, targets=self.targets, block=self.block)
    
    def get(self, key_s):
        """get object(s) by `key_s` from remote namespace
        will return one object if it is a key.
        It also takes a list of keys, and will return a list of objects."""
        # block = block if block is not None else self.block
        return self.client.pull(key_s, block=self.block, targets=self.targets)
    
    push = update
    pull = get
    
    def __getitem__(self, key):
        return self.get(key)
    
    def __setitem__(self,key,value):
        self.update({key:value})
    
    def clear(self):
        """clear the remote namespace"""
        return self.client.clear(targets=self.targets,block=self.block)
    
    def abort(self):
        return self.client.abort(targets=self.targets,block=self.block)

class LoadBalancedView(View):
    _targets=None
    
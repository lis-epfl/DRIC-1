def noplot(no_plot=True):
    def noplot_wrap(func):
        func.noplot = no_plot
        return func
    return noplot_wrap

def withcontext():
    """
    This datasource require a dict context.
    A valid context MAY possess the following key:
    - string 'cid', the client id
    - float 'start', the time at which the connection was made, in seconds
    The datasource should not assume a valid context. It should not assume the presence of a context at all. 
    """
    def with_context_wrap(func):
        func.withcontext = True
        return func
    return with_context_wrap
import itertools
from mercurial import context, util
from mercurial.i18n import _
import mercurial.node as dpynode


# I've took this from http://stackoverflow.com/questions/2551719/mercurial-hook-to-disallow-committing-large-binary-files
# but there are more references to this hook here:
# http://www.selenic.com/pipermail/mercurial/2009-January/023322.html#
#
# to enable, add the following into .hgrc:
#
# [hooks]
# pretxncommit = python:DjHDGutils.hg.hooks.newbinsize
# pretxnchangegroup = python:DjHDGutils.hg.hooks.newbinsize
#
# [limits]
# maxnewbinsize = 10000
#
#
def newbinsize(ui, repo, node=None, **kwargs):
    '''forbid to add binary files over a given size'''
    forbid = False
    # default limit is 10 MB
    limit = int(ui.config('limits', 'maxnewbinsize', 10000000))
    ctx = repo[node]
    for rev in xrange(ctx.rev(), len(repo)):
        ctx = context.changectx(repo, rev)

        # do not check the size of files that have been removed
        # files that have been removed do not have filecontexts
        # to test for whether a file was removed, test for the existence of a filecontext
        filecontexts = list(ctx)
        def file_was_removed(f):
            """Returns True if the file was removed"""
            if f not in filecontexts:
                return True
            else:
                return False

        for f in itertools.ifilterfalse(file_was_removed, ctx.files()):
            fctx = ctx.filectx(f)
            filecontent = fctx.data()
            # check only for new files
            if not fctx.parents():
                if len(filecontent) > limit and util.binary(filecontent):
                    msg = 'new binary file %s of %s is too large: %ld > %ld\n'
                    hname = dpynode.short(ctx.node())
                    ui.write(_(msg) % (f, hname, len(filecontent), limit))
                    forbid = True
    return forbid


# def nopull(ui, repo, source, **kwargs):
#     '''act as a gateway by forbiding any traffic except push

#     The reason is that even if the transaction did not terminate,
#     the revs can be transiently seen. So only allow the owner to
#     push to another repo. See hgbook 10.3.
#     '''
#     if source != 'push':
#         return True
#     return False

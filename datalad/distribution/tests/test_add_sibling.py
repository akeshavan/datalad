# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test adding sibling(s) to a dataset

"""

import os
from os.path import join as opj, abspath, basename
from ..dataset import Dataset
from datalad.api import install, add_sibling
from datalad.distribution.install import get_containing_subdataset
from datalad.utils import chpwd
from datalad.support.gitrepo import GitRepo
from datalad.support.annexrepo import AnnexRepo

from nose.tools import ok_, eq_, assert_false, assert_is_instance
from datalad.tests.utils import with_tempfile, assert_in, with_tree,\
    with_testrepos, assert_not_in
from datalad.tests.utils import SkipTest
from datalad.tests.utils import assert_cwd_unchanged, skip_if_on_windows
from datalad.tests.utils import assure_dict_from_str, assure_list_from_str
from datalad.tests.utils import ok_generator
from datalad.tests.utils import assert_not_in
from datalad.tests.utils import assert_raises
from datalad.tests.utils import ok_startswith
from datalad.tests.utils import skip_if_no_module, skip_if, skip_if_on_windows
from datalad.tests.utils import ok_clean_git


@with_testrepos('submodule_annex', flavors=['local'])
@with_tempfile(mkdir=True)
def test_add_sibling(origin, repo_path):

    # prepare src
    source = install(path=repo_path, source=origin, recursive=True)
    # TODO: For now, circumnavigate the detached head issue.
    # Figure out, what to do.
    for subds in source.get_dataset_handles(recursive=True):
        AnnexRepo(opj(repo_path, subds), init=True,
                  create=False).git_checkout("master")

    res = add_sibling(dataset=source, sibling="test-remote",
                      url="http://some.remo.te/location")
    eq_(res, [basename(source.path)])
    assert_in("test-remote", source.repo.git_get_remotes())
    eq_("http://some.remo.te/location",
        source.repo.git_get_remote_url("test-remote"))

    # doing it again doesn't do anything
    res = add_sibling(dataset=source, sibling="test-remote",
                      url="http://some.remo.te/location")
    eq_(res, [])
    assert_in("test-remote", source.repo.git_get_remotes())
    eq_("http://some.remo.te/location",
        source.repo.git_get_remote_url("test-remote"))

    # fail with conflicting url:
    with assert_raises(RuntimeError) as cm:
        add_sibling(dataset=source, sibling="test-remote",
                    url="http://some.remo.te/location/elsewhere")
    assert_in("""'test-remote' already exists with conflicting URL""",
              str(cm.exception))

    # don't fail with conflicting url, when using force:
    res = add_sibling(dataset=source, sibling="test-remote",
                      url="http://some.remo.te/location/elsewhere", force=True)
    eq_(res, [basename(source.path)])
    eq_("http://some.remo.te/location/elsewhere",
        source.repo.git_get_remote_url("test-remote"))

    # TODO: pushurl
    # TODO: recursive




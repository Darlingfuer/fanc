"""

KaiC
====

Provides
    1. Classes for working with Hi-C data
    2. Classes for working with tabular data

"""
from .version import __version__

from kaic.data.genomic import Hic, Node, Edge, Genome, Chromosome, Bed, AccessOptimisedHic, load_hic, GenomicRegion
from kaic.data.general import Table, FileBased
from kaic.data.registry import class_id_dict
from kaic.construct.seq import Reads, FragmentMappedReadPairs
from kaic.architecture.hic_architecture import DirectionalityIndex, InsulationIndex, PossibleContacts, \
    ExpectedContacts, RegionContactAverage, FoldChangeMatrix, ObservedExpectedRatio, ABDomains, \
    ABDomainMatrix, MetaArray, MetaHeatmap, VectorDifference, VectorArchitecturalRegionFeature, \
    MultiVectorArchitecturalRegionFeature
from kaic.data.network import RaoPeakInfo
from kaic.architecture.genome_architecture import GenomicTrack
import tables
import logging

logging.basicConfig(level=logging.INFO)


def load(file_name, mode='a', tmpdir=None):
    import os
    file_name = os.path.expanduser(file_name)
    try:
        f = FileBased(file_name, mode='r')
        classid = None
        try:
            classid = f.meta._classid
            f.close()
            cls_ = class_id_dict[classid]
            logging.info("Detected {}".format(cls_))
            return cls_(file_name=file_name, mode=mode, tmpdir=tmpdir)
        except AttributeError:
            # try to detect from file structure

            # Hi-C
            try:
                n = f.file.get_node('/edges')
                from kaic.data.general import MaskedTable
                hic_class = None
                if isinstance(n, MaskedTable):
                    hic_class = Hic
                elif isinstance(n, tables.group.Group):
                    hic_class = AccessOptimisedHic

                if hic_class is not None:
                    f.close()
                    return hic_class(file_name, mode=mode, tmpdir=tmpdir)
            except tables.NoSuchNodeError:
                pass

            # others
            detectables = (
                ('insulation_index', InsulationIndex),
                ('directionality_index', DirectionalityIndex),
                ('contact_average', RegionContactAverage),
                ('expected_contacts', FoldChangeMatrix),
                ('distance_decay', ExpectedContacts),
                ('observed_expected', ObservedExpectedRatio),
                ('ab_domains', ABDomains),
                ('ab_domain_matrix', ABDomainMatrix),
                ('possible_contacts', PossibleContacts),
                ('meta_matrix', MetaArray),
                ('meta_heatmap', MetaHeatmap),
                ('tracks', GenomicTrack),
                ('fragments', FragmentMappedReadPairs),
                ('reads', Reads),
                ('vector_diff', VectorDifference),
                ('region_data', VectorArchitecturalRegionFeature),
                ('array_region_data', MultiVectorArchitecturalRegionFeature),
            )

            for name, cls in detectables:
                try:
                    f.file.get_node('/' + name)
                    f.close()
                    return cls(file_name, mode=mode, tmpdir=tmpdir)
                except tables.NoSuchNodeError:
                    pass

            f.close()
            raise ValueError("File ({}) does not have a '_classid' meta attribute. This might be fixed by loading the "
                             "class once explicitly with the appropriate class in append mode. "
                             "It was also impossible to auto-detect the file type from the file "
                             "structure.".format(file_name))
        except KeyError:
            raise ValueError("classid attribute ({}) does not have a registered class.".format(classid))
    except tables.HDF5ExtError:
        # try some well-known file types
        import pybedtools
        f = Bed(file_name)
        try:
            _ = f.file_type
            return f
        except IndexError:
            pass

        try:
            import pyBigWig
            f = pyBigWig.open(file_name, 'r')
            if mode != 'r':
                f.close()
                f = pyBigWig.open(file_name, mode)
            return f
        except (ImportError, RuntimeError):
            raise ValueError("File type not recognised ({}).".format(file_name))


def sample_hic(file_name=None, tmpdir=None):
    hic = Hic(file_name=file_name, tmpdir=tmpdir, mode='w')

    # add some nodes (12 to be exact)
    nodes = []
    for i in range(1, 5000, 1000):
        nodes.append(Node(chromosome="chr1", start=i, end=i+1000-1))
    for i in range(1, 3000, 1000):
        nodes.append(Node(chromosome="chr2", start=i, end=i+1000-1))
    for i in range(1, 2000, 500):
        nodes.append(Node(chromosome="chr3", start=i, end=i+1000-1))
    hic.add_nodes(nodes)

    # add some edges with increasing weight for testing
    edges = []
    weight = 1
    for i in range(0, len(nodes)):
        for j in range(i, len(nodes)):
            edges.append(Edge(source=i, sink=j, weight=weight))
            weight += 1

    hic.add_edges(edges)

    return hic


def sample_hic_big(file_name=None, tmpdir=None):
    hic = Hic(file_name=file_name, tmpdir=tmpdir, mode='w')

    # add some nodes (120 to be exact)
    nodes = []
    for i in range(1, 50000, 1000):
        nodes.append(Node(chromosome="chr1", start=i, end=i + 1000 - 1))
    for i in range(1, 30000, 1000):
        nodes.append(Node(chromosome="chr2", start=i, end=i + 1000 - 1))
    for i in range(1, 20000, 500):
        nodes.append(Node(chromosome="chr3", start=i, end=i + 1000 - 1))
    hic.add_nodes(nodes)

    # add some edges with increasing weight for testing
    edges = []
    weight = 1
    for i in range(0, len(nodes)):
        for j in range(i, len(nodes)):
            edges.append(Edge(source=i, sink=j, weight=weight))
            weight += 1

    hic.add_edges(edges)

    return hic


def sample_fa_hic(file_name=None, tmpdir=None):
    hic = AccessOptimisedHic(file_name=file_name, tmpdir=tmpdir, mode='w')

    # add some nodes (120 to be exact)
    nodes = []
    for i in range(1, 50000, 1000):
        nodes.append(Node(chromosome="chr1", start=i, end=i + 1000 - 1))
    for i in range(1, 30000, 1000):
        nodes.append(Node(chromosome="chr2", start=i, end=i + 1000 - 1))
    for i in range(1, 20000, 500):
        nodes.append(Node(chromosome="chr3", start=i, end=i + 1000 - 1))
    hic.add_nodes(nodes)

    # add some edges with increasing weight for testing
    edges = []
    weight = 1
    for i in range(0, len(nodes)):
        for j in range(i, len(nodes)):
            edges.append(Edge(source=i, sink=j, weight=weight))
            weight += 1

    hic.add_edges(edges)

    return hic
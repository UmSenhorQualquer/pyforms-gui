import logging; logger = logging.getLogger(__name__)

from .controls.control_base import ControlBase
from .controls.control_boundingslider import ControlBoundingSlider
from .controls.control_button import ControlButton
from .controls.control_checkbox import ControlCheckBox
from .controls.control_checkboxlist import ControlCheckBoxList
try:
    from .controls.control_codeeditor import ControlCodeEditor
except Exception as e:
    logger.error( e )
    logger.error('ControlCodeEditor will not be work')
    logger.error('QScintilla may be missing')
from .controls.control_combo import ControlCombo
from .controls.control_dir import ControlDir
from .controls.control_dockwidget import ControlDockWidget
from .controls.control_emptywidget import ControlEmptyWidget
from .controls.control_file import ControlFile
from .controls.control_filestree import ControlFilesTree
try:
    from .controls.control_image import ControlImage
except Exception as e:
    logger.error( e )
from .controls.control_label import ControlLabel
from .controls.control_list import ControlList
from .controls.control_matplotlib import ControlMatplotlib
from .controls.control_mdiarea import ControlMdiArea
from .controls.control_number import ControlNumber
try:
    from .controls.control_opengl import ControlOpenGL
except Exception as e:
    logger.error( e )
    logger.error('ControlOpenGL will not work')
from .controls.control_progress import ControlProgress
from .controls.control_slider import ControlSlider
from .controls.control_tableview import ControlTableView
from .controls.control_text import ControlText
from .controls.control_password import ControlPassword
from .controls.control_textarea import ControlTextArea
from .controls.control_toolbox import ControlToolBox
from .controls.control_toolbutton import ControlToolButton
from .controls.control_tree import ControlTree
from .controls.control_treeview import ControlTreeView
from .controls.control_visvis import ControlVisVis
from .controls.control_visvisvolume import ControlVisVisVolume
try:
    from .controls.control_web import ControlWeb
except Exception as e:
    logger.error( e )
    logger.error('ControlWeb will not work')
    logger.error('QtWebEngine may be missing')
from .controls.control_event_timeline.control_eventtimeline import ControlEventTimeline
from .controls.control_events_graph.control_eventsgraph import ControlEventsGraph
try:
    from .controls.control_player.control_player import ControlPlayer
except Exception as e:
    logger.error( e )
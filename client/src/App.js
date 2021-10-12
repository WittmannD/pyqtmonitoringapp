import {
    Box,
    Button, Card,
    CardActions, CardContent, CardMedia, ClickAwayListener,
    Container, createMuiTheme, Fade, FormControlLabel,
    Grid,
    IconButton, LinearProgress, Link,
    makeStyles,
    Paper, Popper, Switch,
    TextField, Typography
} from "@material-ui/core"
import {Map, fromJS} from 'immutable'
import DeleteIcon from '@material-ui/icons/Delete'
import AddIcon from '@material-ui/icons/Add'
import FolderOpenIcon from '@material-ui/icons/FolderOpen'
import ArrowBackIcon from '@material-ui/icons/ArrowBack'
import DoneIcon from '@material-ui/icons/Done'
import ErrorOutlineIcon from '@material-ui/icons/ErrorOutline'
import {Component, useEffect, useRef, useState} from 'react'
import clsx from 'clsx'
import {QWebChannel} from 'qwebchannel'
import {uid} from "uid";
import 'react-perfect-scrollbar/dist/css/styles.css';
import PerfectScrollbar from 'react-perfect-scrollbar';
import PopupState, {bindPopper, bindToggle} from "material-ui-popup-state";


const useStyles = makeStyles((theme) => ({
    root: {
        height: 'calc(100vh - 10px)',
        '& > div': {
            alignContent: 'flex-start'
        },
        '& > div > div:nth-child(1)': {
            height: '60px'
        }
    },
    titlesContainer: {
        overflow: 'hidden',
        maxHeight: 'calc(100vh - 60px - 10px)'
    },
    monitorsContainer : {
        overflow: 'hidden',
        maxHeight: 'calc(100vh - 60px - 10px)'
    },
    monitorCard: {
        padding: theme.spacing(2),
        marginBottom: theme.spacing(2),
        backgroundColor: 'rgba(250, 250, 250, 1)',
        backgroundImage: 'linear-gradient(0deg, rgba(247,247,247,1) 0%, rgba(231,231,231,1) 100%)',
        cursor: 'pointer'
    },
    card: {
        display: 'flex',
        marginBottom: theme.spacing(2),
        backgroundColor: 'rgba(250, 250, 250, 1)',
        backgroundImage: 'linear-gradient(0deg, rgba(247,247,247,1) 0%, rgba(231,231,231,1) 100%)',
        height: '200px'
    },
    monitorCardSelected: {
        backgroundImage: 'linear-gradient(0deg, rgba(228,243,255,1) 0%, rgba(211,227,253,1) 100%)'
    },
    tabCount: {
        marginBottom: '10px',
        marginRight: '10px'
    },
    flexExpand: {
        flexGrow: 1
    },
    delete: {
        color: theme.palette.error.light
    },
    add: {
        color: theme.palette.text.secondary
    },
    success: {
        color: theme.palette.success.dark
    },
    error: {
        color: theme.palette.error.dark
    },
    back: {
        color: theme.palette.text.secondary
    },
    openInExplorer: {
        color: 'rgba(255, 255, 255, 0.75)'
    },
    cardCover: {
        flexBasis: '30%',
        flexShrink: 0,
        flexGrow: 0,
        position: "relative"
    },
    cardContent: {
        flexGrow: 1
    },
    bullet: {
        display: 'inline-block',
        margin: '0 4px',
        transform: 'scale(0.8)',
    },
    elide: {
        overflow: 'hidden',
        whiteSpace: 'nowrap',
        textOverflow: 'ellipsis'
    },
    altTitles: {
        overflow: 'hidden',
        display: '-webkit-box',
        boxOrient: 'vertical',
        lineClamp: 2
    },
    fixed: {
        position: 'fixed'
    },
    formDetail: {
        color: 'rgba(0, 0, 0, 0.26)',
        fontSize: '0.6em',
        textTransform: 'uppercase'
    }
}))


function MonitorCard(props) {

    const classes = useStyles()

    const [selected, setSelected] = useState(props.data.get('selected'))

    useEffect(() => {
        setSelected(props.data.get('selected'))
    }, [props.data])


    return (
        props.defaultMonitor ?
            <Paper elevation={0} className={classes.monitorCard} onClick={props.onClick}>
                <Typography variant="body1" component="h3">
                    { props.data.get('name') }
                </Typography>
                <Typography variant="caption" component="p">
                    { props.data.get('description') }
                </Typography>
            </Paper>
        :
            <Paper
                className={clsx(classes.monitorCard, {
                    [classes.monitorCardSelected]: selected
                })}
                onClick={props.onClick}
                elevation={0}
            >
                <Typography variant="body1" component="h3">
                    { props.data.getIn(['options', 'name']) }
                </Typography>
                <Typography variant="caption" component="p">
                    { props.data.getIn(['options', 'description']) }
                </Typography>
                <Box sx={{ width: '100%' }} mt={2} >
                  <LinearProgress color="secondary" />
                </Box>
            </Paper>
    )
}


function TitleCard(props) {

    const classes = useStyles()


    function getDatetimeString(unixTimestamp, inMs=false) {
        let milliseconds = unixTimestamp
        if (!inMs)
            milliseconds = Math.ceil(unixTimestamp * 1000)
        const dateObject = new Date(milliseconds)
        return dateObject.toLocaleString()
    }

    const titleLink = "http://seoji.nl.go.kr/landingPage?isbn=" + props.data.getIn(['title', 'isbn'])
    const coverPath = () => {
        let path = decodeURI(props.data.getIn(['title', 'cover']))
        return new URL(`file:///${path}`).href
    }

    return (
        <Card className={classes.card} elevation={0} >
            <CardMedia
                className={classes.cardCover}
                image={coverPath()}
                title="cover"
            >
                <Box position="absolute" top={0} left={0} p={1}>
                    <IconButton
                        size="small"
                        className={classes.openInExplorer}
                        onClick={(e) => {
                            props.openInExplorer(coverPath())
                        }}
                    >
                        <FolderOpenIcon fontSize="small"/>
                    </IconButton>
                </Box>
                {props.data.getIn(['info', 'status']) &&
                    <Box position="absolute" top={0} right={0} p={1}>
                        <PopupState variant="popper" popupId="demo-popup-popper">
                            {(popupState) => (
                                <div>
                                    {
                                        props.data.getIn(['info', 'status']) === 'success' &&
                                        <IconButton
                                            size="small"
                                            className={classes.success}
                                            {...bindToggle(popupState)}
                                        >
                                            <DoneIcon fontSize="small"/>
                                        </IconButton>
                                    }
                                    {
                                        props.data.getIn(['info', 'status']) === 'error' &&
                                        <IconButton
                                            size="small"
                                            className={classes.error}
                                            {...bindToggle(popupState)}
                                        >
                                            <ErrorOutlineIcon fontSize="small"/>
                                        </IconButton>
                                    }

                                    <Popper {...bindPopper(popupState)}  >
                                        <ClickAwayListener onClickAway={popupState.close}>
                                            <Paper>
                                                <Box sx={{p: 2}}>
                                                    <Typography variant="body2" gutterBottom>
                                                        <i>
                                                            {
                                                                getDatetimeString(
                                                                    props.data.getIn(['info', 'timestamp']),
                                                                    true
                                                                )
                                                            }
                                                        </i>
                                                        : {props.data.getIn(['info', 'status'])}
                                                    </Typography>
                                                    <Typography variant="body2">
                                                        {props.data.getIn(['info', 'message'])}
                                                    </Typography>

                                                </Box>
                                            </Paper>

                                        </ClickAwayListener>

                                    </Popper>
                                </div>
                            )}
                        </PopupState>

                    </Box>
                }
            </CardMedia>
            <Box display="flex" width="70%" flexDirection="column">
                <CardContent className={classes.cardContent}>
                    <Box display="flex" justifyContent="space-between">
                        <Typography variant="caption" className={clsx(classes.formDetail, classes.elide)} title="form detail">
                            <span style={{'display': 'inline-block', 'width': '110px'}}>
                                form: <b>{props.data.getIn(['title', 'description', 3])}</b>
                            </span>
                            <span>publisher: <b>{props.data.getIn(['title', 'description', 2])}</b></span>
                        </Typography>
                        <Typography variant="caption" component="div" align="right" style={{"flex": "1 0 150px"}}>
                            <span>{getDatetimeString(props.data.getIn(['title', 'timestamp']))}</span>
                        </Typography>
                    </Box>
                    <Typography variant="body1" component="h3" className={classes.elide}>
                        {props.data.getIn(['title', 'rus_title'])}
                    </Typography>
                    <Typography variant="caption" component="h4" gutterBottom className={classes.altTitles}>
                        <span>
                            {props.data.getIn(['title', 'eng_title'])}
                        </span>
                        <span className={classes.bullet}>•</span>
                        <span>
                            {props.data.getIn(['title', 'kor_title'])}
                        </span>
                    </Typography>
                    <Typography>
                        <Link
                            href={titleLink}
                            onClick={(e) => {
                                props.openInBrowser(titleLink)
                                e.preventDefault();
                            }}
                            variant="caption"
                        >
                            ISBN {props.data.getIn(['title', 'isbn'])}
                        </Link>
                    </Typography>
                </CardContent>
                <CardActions>
                    <Button
                        onClick={props.send}
                        className={clsx(classes.flexExpand)}
                    >
                        Fill Form
                    </Button>
                    <Button
                        onClick={props.remove}
                        startIcon={
                            <DeleteIcon className={classes.delete}/>
                        }
                    >
                        Delete
                    </Button>
                </CardActions>
            </Box>
        </Card>
    )
}

function App() {
    const classes = useStyles()

    const titlesRef = useRef(Map())
    const [tabsCount, setTabsCount] = useState(0)
    const [monitors, setMonitors] = useState(Map())
    const [defaultMonitors, setDefaultMonitors] = useState(Map())
    const [titles, setTitles] = useState(Map())

    const [state, setState] = useState({
        tabsCountValue: 1,
        autoMode: true
    })

    const [addMonitorTab, setAddMonitorTab] = useState(false)

    const createTabs = (e) => {
        window.Controller.createTabsEmit(state.tabsCountValue)
    }

    const addMonitor = (monitor) => {
        window.Controller.addMonitorEmit(JSON.stringify({
            uid: uid(16),
            name: monitor.get('name'),
            keyword: monitor.getIn(['payload', 'q']),
            description: monitor.get('description'),
            timeout: monitor.get('timeout'),
            check_every: monitor.get('check_every'),
            method: monitor.get('method'),
            url: monitor.get('url'),
            payload: monitor.get('payload').toJS()
        }))
    }

    const removeMonitors = (e) => {
        let unselectedMonitors = Map()
        monitors.forEach((value, key, map) => {
            if (value.get('selected')) {
                window.Controller.removeMonitorEmit(key)
            } else {
                unselectedMonitors = unselectedMonitors.set(key, value)
            }
        })

        setMonitors(unselectedMonitors)
    }
    const openInExplorer = (path) => window.Controller.openCoverInExplorerEmit(path)
    const openInBrowser = (link) => window.Controller.openLinkInBrowserEmit(link)

    const addTitleForSend = (title) =>
        window.Controller.addTitleForSendEmit(
            JSON.stringify(['client', title.get('title').toJS()])
        )

    const removeTitle = (uid) => setTitles(titles => titles.delete(uid))

    const tabsCountChange = (e) => setState(state => ({tabsCountValue: e.target.value, autoMode: state.autoMode}))
    const autoModeChange = (e) => setState(state => ({tabsCountValue: state.tabsCountValue, autoMode: e.target.checked}))

    useEffect(() => {
        window.Controller.changeAutoModeEmit(state.autoMode)
    }, [state.autoMode])

    useEffect(() => {
        window.Controller.getInitialData((data) => {
            data = JSON.parse(data)
            setDefaultMonitors(defaultMonitors => fromJS(data.monitors))
        })

        const storedTitles = JSON.parse(window.localStorage.getItem('titles'))

        if (storedTitles)
            setTitles(fromJS(storedTitles))

        window.Controller.commitTab.connect((v) => {
            setTabsCount(tabsCount => tabsCount + (-1) ** (!v))
        })

        window.Controller.commitTitle.connect((data) => {
            let title = JSON.parse(data)
            setTitles(titles => titles.set(
                title.uid,
                fromJS({info: {status: null, message: null, timestamp: null}, title})
            ))
        })

        window.Controller.setTitleStatus.connect((data) => {
            let info = fromJS(JSON.parse(data))
            setTitles(titles => titles.updateIn(
                [info.get(0), 'info'],
                dict => info.get(1)
            ))
        })

        window.Controller.commitMonitor.connect((data) => {
            let monitor = JSON.parse(data)
            setMonitors(monitors => monitors.set(monitor.uid, fromJS({selected: false, options: monitor})))
        })

        const storedState = JSON.parse(window.localStorage.getItem('state'))

        if (storedState)
            setState(storedState)

    }, [])

    useEffect(() => {
        window.localStorage.setItem('titles', JSON.stringify(titles.toJS()))
    }, [titles])

    useEffect(() => {
        window.localStorage.setItem('state', JSON.stringify(state))
    }, [state])



    return (
        <Container maxWidth="lg">
            <Grid container spacing={2} className={classes.root}>
                <Grid item container xs={12} sm={4} spacing={2} style={{'height': '100%'}}>
                    {
                        addMonitorTab ?
                            <>
                                <Grid item xs={12}>
                                    <IconButton
                                        aria-label="back"
                                        size="medium"
                                        className={classes.back}
                                        onClick={() => { setAddMonitorTab(false) }}>
                                        <ArrowBackIcon fontSize="small"/>
                                    </IconButton>
                                </Grid>
                                <Grid item xs={12} spacing={0} style={{'height': 'calc(100% - 60px)'}}>
                                    <PerfectScrollbar options={{suppressScrollX: false}} style={{width: '100%'}}>
                                        {
                                            defaultMonitors.map(monitor =>
                                                <MonitorCard
                                                    data={monitor}
                                                    key={monitor.get('uid')}
                                                    defaultMonitor={true}
                                                    onClick={(e) => {
                                                        addMonitor(monitor)
                                                        setAddMonitorTab(false)
                                                    }}
                                                />
                                            )
                                        }
                                    </PerfectScrollbar>
                                </Grid>
                            </>
                        :
                            <>
                                <Grid item xs={12}>
                                    <IconButton
                                        aria-label="add"
                                        size="medium"
                                        className={classes.add}
                                        onClick={() => {setAddMonitorTab(true)}}>
                                        <AddIcon fontSize="small"/>
                                    </IconButton>
                                    <IconButton
                                        aria-label="delete"
                                        size="medium"
                                        className={classes.delete}
                                        onClick={removeMonitors}>
                                        <DeleteIcon fontSize="small"/>
                                    </IconButton>
                                </Grid>
                                <Grid item xs={12} spacing={0} style={{'height': 'calc(100% - 60px)'}}>
                                    <PerfectScrollbar options={{suppressScrollX: false}} style={{width: '100%'}}>
                                        {
                                            monitors.entrySeq().map(([key, value], i) =>
                                                <MonitorCard
                                                    data={value}
                                                    onClick={
                                                        () => {
                                                            setMonitors(
                                                                monitors.update(key, monitor =>
                                                                    monitor.set('selected', !monitor.get('selected')))
                                                            )
                                                        }
                                                    }
                                                    key={key}
                                                />
                                            )
                                        }
                                    </PerfectScrollbar>
                                </Grid>
                            </>
                    }
                </Grid>
                <Grid item container xs={12} sm={8} spacing={2} style={{'height': '100%'}}>
                    <Grid item container xs={12} justifyContent="space-between" alignContent="center">
                        <Box display="flex" alignItems="center" flexBasis="55%">
                            <TextField
                                label="Tabs Count"
                                type="number"
                                value={state.tabsCountValue}
                                onChange={tabsCountChange}
                                InputLabelProps={{'shrink': true}}
                                InputProps={{
                                    inputProps: {
                                        max: 14, min: 1
                                    }
                                }}
                                size="small"
                                fullWidth
                                className={classes.tabCount}
                            />
                            <Button onClick={createTabs}>create</Button>
                        </Box>
                        <Box display="flex" alignItems="center">
                            <FormControlLabel
                                value="start"
                                control={
                                    <Switch
                                        color="primary"
                                        checked={state.autoMode}
                                        onChange={autoModeChange}
                                    />
                                }
                                label="Auto mode"
                                labelPlacement="start"
                            />
                        </Box>

                    </Grid>
                    <Grid item xs={12} spacing={0} style={{'height': 'calc(100% - 60px)'}}>
                        <PerfectScrollbar options={{suppressScrollX: false}} style={{'width': '100%'}}>
                            {
                                titles.sortBy(o => -o.getIn(['title', 'timestamp'])).entrySeq().map(
                                    ([key, value]) =>
                                        <TitleCard
                                            data={value}
                                            key={key}
                                            remove={(e) => removeTitle(key)}
                                            send={(e) => addTitleForSend(value)}
                                            openInBrowser={openInBrowser}
                                            openInExplorer={openInExplorer}
                                        />
                                )
                            }
                        </PerfectScrollbar>
                    </Grid>
                </Grid>
            </Grid>
        </Container>

    )
}

export default App

import moment from 'moment';
import { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useIntl } from 'react-intl';

import { useMediaQuery, Box, Dialog, SpeedDial, Tooltip } from '@mui/material';

import FullCalendar from '@fullcalendar/react';
import esLocale from '@fullcalendar/core/locales/es';
import interactionPlugin from '@fullcalendar/interaction';
import listPlugin from '@fullcalendar/list';

import CalendarStyled from 'sections/dimmingcalendar/CalendarStyled';
import Toolbar from 'sections/dimmingcalendar/Toolbar';
import AddDimmingEventForm from 'sections/dimmingcalendar/AddDimmingEventForm';
import { getEvents, selectEvent, selectRange, toggleModal, updateDimmingCalendarView, updateEvent } from 'store/reducers/dimmingCalendar';

import { PlusOutlined } from '@ant-design/icons';

const selectedEventHandler = (state) => {
  const { events, selectedEventId } = state.dimmingCalendar;
  if (selectedEventId) {
    return events.find((event) => event.id === selectedEventId);
  }
  return null;
};

const Calendar = () => {
  const intl = useIntl();
  const matchDownSM = useMediaQuery((theme) => theme.breakpoints.down('sm'));
  const dispatch = useDispatch();
  const calendar = useSelector((state) => state.dimmingCalendar);
  const { calendarView, events, isModalOpen, selectedRange } = calendar;
  const selectedEvent = useSelector(selectedEventHandler);

  useEffect(() => {
    dispatch(getEvents());
  }, [dispatch]);

  const calendarRef = useRef(null);

  useEffect(() => {
    const calendarEl = calendarRef.current;
    if (calendarEl) {
      const calendarApi = calendarEl.getApi();
      const newView = 'listWeek';
      calendarApi.changeView(newView);
      dispatch(updateDimmingCalendarView(newView));
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [matchDownSM]);

  const [date, setDate] = useState(new Date());

  const handleDateToday = () => {
    const calendarEl = calendarRef.current;

    if (calendarEl) {
      const calendarApi = calendarEl.getApi();
      calendarApi.today();
      setDate(calendarApi.getDate());
    }
  };

  const handleDatePrev = () => {
    const calendarEl = calendarRef.current;

    if (calendarEl) {
      const calendarApi = calendarEl.getApi();

      calendarApi.prev();
      setDate(calendarApi.getDate());
    }
  };

  const handleDateNext = () => {
    const calendarEl = calendarRef.current;

    if (calendarEl) {
      const calendarApi = calendarEl.getApi();

      calendarApi.next();
      setDate(calendarApi.getDate());
    }
  };

  // calendar events
  const handleRangeSelect = (arg) => {
    const calendarEl = calendarRef.current;
    if (calendarEl) {
      const calendarApi = calendarEl.getApi();
      calendarApi.unselect();
    }
    dispatch(selectRange(arg.start, arg.end));
  };

  const handleEventSelect = (arg) => {
    dispatch(selectEvent(arg.event.id));
  };

  const handleEventUpdate = async ({ event }) => {
    try {
      dispatch(
        updateEvent(event.id, {
          allDay: event.allDay,
          start: event.start,
          end: event.end
        })
      );
    } catch (error) {
      console.error(error);
    }
  };

  const handleModal = () => {
    dispatch(toggleModal());
  };

  const mkTitle = (e) => {
    if (e.command.startsWith('dim')) {
      const val = e.command.split('_')[1];
      return intl.formatMessage({ id: 'dimmingCalendar.event.dim-all-to.title' }, { percentage: val });
    }
    if (e.command == 'turn_on') return intl.formatMessage({ id: 'dimmingCalendar.event.turn-on-all.title' });
    if (e.command == 'turn_off') return intl.formatMessage({ id: 'dimmingCalendar.event.turn-off-all.title' });
  };

  const fromApiEvent = (e) => {
    return {
      id: e.id,
      title: mkTitle(e),
      description: e.command,
      color: e.color,
      textColor: e.textColor,
      allDay: false,
      date: e.start,
      startTime: moment(e.start).format('HH:mm:ss'),
      endTime: moment(e.end).format('HH:mm:ss'),
      startRecur: e.start
    };
  };

  return (
    <Box sx={{ position: 'relative' }}>
      <CalendarStyled>
        <Toolbar date={date} onClickNext={handleDateNext} onClickPrev={handleDatePrev} onClickToday={handleDateToday} />

        <FullCalendar
          locale={intl.locale == 'es' ? esLocale : 'en'}
          weekends
          editable
          droppable
          selectable
          events={events.map(fromApiEvent)}
          ref={calendarRef}
          rerenderDelay={10}
          initialDate={date}
          initialView={calendarView}
          eventDisplay="block"
          headerToolbar={false}
          allDayMaintainDuration
          eventResizableFromStart
          select={handleRangeSelect}
          eventDrop={handleEventUpdate}
          eventClick={handleEventSelect}
          eventResize={handleEventUpdate}
          height={matchDownSM ? 'auto' : 720}
          plugins={[listPlugin, interactionPlugin]}
        />
      </CalendarStyled>

      {/* Dialog renders its body even if not open */}
      <Dialog maxWidth="sm" fullWidth onClose={handleModal} open={isModalOpen} sx={{ '& .MuiDialog-paper': { p: 0 } }}>
        {isModalOpen && <AddDimmingEventForm event={selectedEvent} range={selectedRange} onCancel={handleModal} />}
      </Dialog>
      <Tooltip title="Add New Event">
        <SpeedDial
          ariaLabel="add-event-fab"
          sx={{ display: 'inline-flex', position: 'sticky', bottom: 24, left: '100%', transform: 'translate(-50%, -50% )' }}
          icon={<PlusOutlined style={{ fontSize: '1.5rem' }} />}
          onClick={handleModal}
        />
      </Tooltip>
    </Box>
  );
};

export default Calendar;

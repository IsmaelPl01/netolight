import { createSlice } from '@reduxjs/toolkit';

import _ from 'lodash';
import humps from 'humps';

import axios from 'utils/axios';
import { dispatch } from 'store';

const initialState = {
  calendarView: 'listWeek',
  error: false,
  events: [],
  isLoader: false,
  isModalOpen: false,
  selectedEventId: null,
  selectedRange: null
};

const dimmingCalendar = createSlice({
  name: 'dimmingCalendar',
  initialState,
  reducers: {
    loading(state) {
      state.isLoader = true;
    },

    hasError(state, action) {
      state.isLoader = false;
      state.error = action.payload;
    },

    setEvents(state, action) {
      state.isLoader = false;
      state.events = action.payload;
    },

    updateDimmingCalendarView(state, action) {
      state.calendarView = action.payload;
    },

    selectEvent(state, action) {
      const eventId = action.payload;
      state.isModalOpen = true;
      state.selectedEventId = parseInt(eventId);
    },

    createEvent(state, action) {
      const newEvent = action.payload;
      state.isLoader = false;
      state.isModalOpen = false;
      state.events = [...state.events, newEvent];
    },

    updateEvent(state, action) {
      const event = action.payload;
      const eventUpdate = state.events.map((item) => {
        if (item.id === event.id) {
          return event;
        }
        return item;
      });

      state.isLoader = false;
      state.isModalOpen = false;
      state.events = eventUpdate;
    },

    deleteEvent(state, action) {
      const eventId = action.payload;
      state.isModalOpen = false;
      const deleteEvent = state.events.filter((event) => {
        return event.id !== eventId;
      });
      state.events = deleteEvent;
    },

    selectRange(state, action) {
      const { start, end } = action.payload;
      state.isModalOpen = true;
      state.selectedRange = { start, end };
    },

    toggleModal(state) {
      state.isModalOpen = !state.isModalOpen;
      if (state.isModalOpen === false) {
        state.selectedEventId = null;
        state.selectedRange = null;
      }
    }
  }
});

export default dimmingCalendar.reducer;

export const { selectEvent, toggleModal, updateDimmingCalendarView } = dimmingCalendar.actions;

export function getEvents() {
  return async () => {
    dispatch(dimmingCalendar.actions.loading());
    try {
      const response = await axios.get('/api/dimming_events/');
      dispatch(dimmingCalendar.actions.setEvents(humps.camelizeKeys(response.data.data)));
    } catch (error) {
      dispatch(dimmingCalendar.actions.hasError(error));
    }
  };
}

export function createEvent(newEvent) {
  return async () => {
    dispatch(dimmingCalendar.actions.loading());
    try {
      const response = await axios.post('/api/dimming_events/', humps.decamelizeKeys(newEvent));
      dispatch(dimmingCalendar.actions.createEvent(_.merge({}, response.data, newEvent)));
    } catch (error) {
      dispatch(dimmingCalendar.actions.hasError(error));
    }
  };
}

export function updateEvent(eventId, updateEvent) {
  return async () => {
    dispatch(dimmingCalendar.actions.loading());
    try {
      await axios.put(`/api/dimming_events/${eventId}`, humps.decamelizeKeys(updateEvent));
      dispatch(dimmingCalendar.actions.updateEvent(_.merge({ id: eventId }, updateEvent)));
    } catch (error) {
      dispatch(dimmingCalendar.actions.hasError(error));
    }
  };
}

export function deleteEvent(eventId) {
  return async () => {
    dispatch(dimmingCalendar.actions.loading());
    try {
      await axios.delete(`/api/dimming_events/${eventId}`);
      dispatch(dimmingCalendar.actions.deleteEvent(eventId));
    } catch (error) {
      dispatch(dimmingCalendar.actions.hasError(error));
    }
  };
}

export function selectRange(start, end) {
  return async () => {
    dispatch(
      dimmingCalendar.actions.selectRange({
        start: start.getTime(),
        end: end.getTime()
      })
    );
  };
}

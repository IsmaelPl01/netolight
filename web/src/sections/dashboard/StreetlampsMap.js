/* eslint-disable */
import React from 'react'
import { GoogleMap, MarkerClusterer, MarkerF, useJsApiLoader } from '@react-google-maps/api';

const containerStyle = {
  width: '100%',
  height: '500px'
};

const center = {
  lat: 18.483402,
  lng: -69.929611
};

const options = {
  imagePath:
    'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'
};

const createKey = (location) => location.lat + location.lng


function StreetlampsMap({ streetlamps }) {
  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: 'AIzaSyBrz4esLi4QAfGSmP3oPvU0F_sqFaVgvVY'
  })

  const [map, setMap] = React.useState(null);

  const locations = streetlamps.map((s) => ({lat: s.lat, lng: s.lon}));

  const onLoad = React.useCallback(function callback(map) {
    setMap(map)
  }, [])

  const onUnmount = React.useCallback(function callback(map) {
    setMap(null)
  }, [])

  return isLoaded ? (
      <GoogleMap
        mapContainerStyle={containerStyle}
        center={center}
        zoom={10}
        onLoad={onLoad}
        onUnmount={onUnmount}
      >
         <MarkerClusterer options={options}>
          {(clusterer) => (
            <>
              {locations.map((location) => (
                <MarkerF
                  key={createKey(location)}
                  position={location}
                  clusterer={clusterer}
                />
              ))}
            </>
          )}
        </MarkerClusterer>
      </GoogleMap>
  ) : <></>
}

export default React.memo(StreetlampsMap)

import * as React from "react";

export function useMediaQuery(query) {
  const [value, setValue] = React.useState(true);

  React.useEffect(() => {
    const mediaQueryList = window.matchMedia(query);

    // Define a listener function
    function onChange(event) {
      // In older browsers, event may not have 'matches'
      const isMatch = event.matches !== undefined ? event.matches : mediaQueryList.matches;
      setValue(isMatch);
    }

    // Check if 'addEventListener' exists
    if (mediaQueryList.addEventListener) {
      mediaQueryList.addEventListener('change', onChange);
    } else if (mediaQueryList.addListener) {
      // For older browsers
      mediaQueryList.addListener(onChange);
    }

    // Set the initial value
    setValue(mediaQueryList.matches);

    // Cleanup function
    return () => {
      if (mediaQueryList.removeEventListener) {
        mediaQueryList.removeEventListener('change', onChange);
      } else if (mediaQueryList.removeListener) {
        // For older browsers
        mediaQueryList.removeListener(onChange);
      }
    };
  }, [query]);

  return value;
}

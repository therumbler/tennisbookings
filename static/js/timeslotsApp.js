function tennisTimeslots() {
  return {
    timeslots: [],
    loading: true,
    error: null,

    // Computed property to group timeslots by location
    get groupedTimeslots() {
      const grouped = {};
      this.timeslots.forEach((timeslot) => {
        if (!grouped[timeslot.location_name]) {
          grouped[timeslot.location_name] = [];
        }
        grouped[timeslot.location_name].push(timeslot);
      });
      // Sort locations alphabetically
      const sortedLocations = Object.keys(grouped).sort();
      const sortedGrouped = {};
      sortedLocations.forEach((loc) => {
        // Sort timeslots within each location by datetime
        grouped[loc].sort(
          (a, b) => new Date(a.datetime_str) - new Date(b.datetime_str)
        );
        sortedGrouped[loc] = grouped[loc];
      });
      return sortedGrouped;
    },

    // Function to fetch timeslots from the API
    async fetchTimeslots() {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetch("/api/timeslots");
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        // Basic validation of the incoming data structure
        if (
          Array.isArray(data) &&
          data.every(
            (item) =>
              typeof item.booking_url === "string" &&
              typeof item.court_name === "string" &&
              typeof item.datetime_obj === "string" &&
              typeof item.datetime_str === "string" &&
              typeof item.is_booked === "boolean" &&
              typeof item.location_name === "string"
          )
        ) {
          this.timeslots = data;
        } else {
          throw new Error("Received data is not in the expected format.");
        }
      } catch (e) {
        console.error("Failed to fetch timeslots:", e);
        this.error = "Failed to load timeslots. Please try again later.";
      } finally {
        this.loading = false;
      }
    },

    // Function to format the datetime string for display
    formatDateTime(datetime_str) {
      try {
        const date = new Date(datetime_str);
        // Options for date and time formatting

        const options = {
          weekday: "short", // Mon, Tue, etc.
          month: "short", // Jan, Feb, etc.
          day: "numeric", // 1, 2, etc.
          year: "numeric", // 2023, 2024, etc.
          hour: "numeric", // 1, 2, etc.
          minute: "2-digit", // 00, 30, etc.
          hour12: true, // AM/PM
        };
        const currentYear = new Date().getFullYear();
        if (date.getFullYear() === currentYear) {
          delete options.year; // Remove year if it's the current year
        }

        return date.toLocaleString("en-US", options);
      } catch (e) {
        console.error("Error formatting date:", e);
        return datetime_str; // Return original if formatting fails
      }
    },
  };
}

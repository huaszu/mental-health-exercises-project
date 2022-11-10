if ('Notification' in window) {
    if (Notification.permission === 'granted') {
        const notification = new Notification('Test!');
    } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then((permission) => {
            if (permission === 'granted') {
                const notification = new Notification('Test me');
            }
        });
    }
  }
function commentReplyToggle(parent_id) {
	const row = document.getElementById(parent_id);

	if (row.classList.contains('d-none')) {
		row.classList.remove('d-none');
	} else {
		row.classList.add('d-none');
	}
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}






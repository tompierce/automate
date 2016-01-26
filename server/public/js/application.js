var Automate = {
    
    pollJobs : function() {
        var self = this;
        var xmlHttp = new XMLHttpRequest();

        xmlHttp.onreadystatechange = function() { 
            if (xmlHttp.readyState === 4) {
                if (xmlHttp.status === 200) {
                    self.jobList = JSON.parse(xmlHttp.responseText).job_list;
                    self.updateView()
                } else {
                    self.alert('Failed to poll job list');
                }
               setTimeout(function() { self.pollJobs(); }, 10000);
            }
        }

        var ASYNC = true;
        xmlHttp.open("GET", "/jobs", ASYNC);
        xmlHttp.send(null);
    },

    updateView : function() {
        var self = this;
        var jobTableElement = document.getElementById('jobTable');

        self._removeAllChildren(jobTableElement);

        for (job of self.jobList) {
            jobTableRow = self._createJobTableRow(job);
            jobTableElement.appendChild(jobTableRow);
        }

    },
    
    _createJobTableRow : function() {
        var self = this;
        var job_status_color = 'gray';
        switch (job.last_run_status) {
            case "SUCCESS":
                job_status_color = "green";
                break;
            case "FAILURE":
                job_status_color = "red";
                break;
            case "UNSTABLE":
                job_status_color = "orange";
                break
            default:
                job_status_color = 'gray';
        }

        var jobStr = '';
        if (job.last_run === 'NEVER') {
            jobStr = "Never";
        } else {
            jobStr = moment(job.last_run).fromNow();
        }

        var lastRun = el('A', jobStr)
        lastRun.setAttribute('href', '/logs/' + job.id)

        statusElement = el('DIV', '');
        statusElement.setAttribute('style', 'width:32px; height:32px; background-color:' + job_status_color);
        
        jobTrigger = el('A', 'Execute');
        jobTrigger.setAttribute('href', '#');
        jobTrigger.setAttribute('data-job-id', job.id);
        jobTrigger.addEventListener('click', function(eventObj) {
            var xmlHttp = new XMLHttpRequest();

            xmlHttp.onreadystatechange = function() { 
                if (xmlHttp.readyState === 4) {
                    if (xmlHttp.status === 200) {
                    } else {
                        self.alert('Failed to execute job');
                    }
                }
            }

            var ASYNC = true;
            jobId = eventObj.target.getAttribute('data-job-id');
            xmlHttp.open("POST", "/job/" + jobId, ASYNC);
            xmlHttp.send();
        });

        return el('TR',  [
                    el('TD', [statusElement]), 
                    el('TD', job.name), 
                    el('TD', [lastRun]),
                    el('TD', [jobTrigger])
                ]);
    },

    _removeAllChildren : function(element) {
        while (element.lastChild) {
            element.removeChild(element.lastChild);
        }
    },

    alert : function(msg) {
        var self = this;
        console.error(msg);
    }
};

function el(elementStr, child) {
    var e = document.createElement(elementStr);
    if (child) {
        if (typeof child === 'string') {
            e.appendChild(document.createTextNode(child));
        } else if (Object.prototype.toString.call( child ) === '[object Array]') {
            for (element of child) {
                e.appendChild(element);
            }
        }
    }
    return e;
}


Automate.pollJobs();
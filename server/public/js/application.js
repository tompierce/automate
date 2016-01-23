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

        self._clearJobTable();

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

        for (job of self.jobList) {
            
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

            statusElement = el('DIV', '');
            statusElement.setAttribute('style', 'width:32px; height:32px; background-color:' + job_status_color);
            jobTableElement.appendChild(el('TR', 
                [
                    el('TD', [statusElement]), 
                    el('TD', job.name), 
                    el('TD', jobStr)
                ]));
        }

    },
    
    _clearJobTable : function() {
        var self = this;
        jobTableElement = document.getElementById('jobTable');

        while (jobTableElement.lastChild) {
            jobTableElement.removeChild(jobTableElement.lastChild);
        }
    },

    alert : function(msg) {
        var self = this;
        console.error(msg);
    }
};

Automate.pollJobs();
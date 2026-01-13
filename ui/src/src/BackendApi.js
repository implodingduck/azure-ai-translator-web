class BackendApi {
    baseurl;
    auth;

    constructor(baseurl, auth) {
        this.baseurl = baseurl;
        this.auth = auth;
    }

    async callApi(path, method='GET', data={}){
        const options = {
            method: method,
            headers: {
                "content-type": "application/json",
                "Authorization": `Bearer ${this.auth.user.access_token}`
            }
        };
        
        if (method !== 'GET' && Object.keys(data).length > 0) {
            options.body = JSON.stringify(data);
        }
        console.log(`Calling API: ${this.baseurl}${path} with method ${method} and data`, data);
        
        const response = await fetch(`${this.baseurl}${path}`, options);
        console.log(response)
        const json = await response.json();
        return json;
    }

    async getSupportedLanguages() {
        return this.callApi('/SupportedLanguages');
    }

    async listDirectories() {
        return this.callApi('/directories');
    }

    async listFiles(directory) {
        return this.callApi(`/directories/${directory}`);
    }

    async createDirectory(directory) {
        return this.callApi(`/directories/`, 'POST', {"directory_name": directory});
    }

    async uploadFile(directory, file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const options = {
            method: 'POST',
            headers: {
                "Authorization": `Bearer ${this.auth.user.access_token}`
            },
            body: formData
        };
        
        console.log(`Uploading file to: ${this.baseurl}/UploadFile?directory_name=${directory}`);
        
        const response = await fetch(`${this.baseurl}/UploadFile?directory_name=${directory}`, options);
        
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
        }
        
        const json = await response.json();
        return json;
    }

}

export { BackendApi }
Vue.component('image-form', {
    props: ['imagesIds', 'imageSelected', 'imagesErrors'],
    data() {
        return {
            progressBars: [],
            images: [],
        }
    },
    methods: {
        sendImages: function (event) {
            var th = this;
            var fileInput = event.target;

            for (var k = 0; k < fileInput.files.length; k++) {
                var fd = new FormData();
                fd.append('file', fileInput.files[k]);

                this.progressBars.push(0);
                (function(itemBarNum) {
                    axios({
                        method: 'POST',
                        url: '/image/api/',
                        data: fd,
                        headers: { 'X-CSRFToken': _gl.getCSRFToken(), 'Content-Type': 'multipart/form-data' },
                        onUploadProgress: function(event) {
                          var percent = Math.round( (event.loaded * 100) / event.total);
                          th.progressBars[itemBarNum] = percent;
                        }
                    })
                    .then(function (response) {
                        if (_.isObject(response.data)) {
                            var newImagesIds = _.clone(th.imagesIds)
                            newImagesIds.push(response.data.id)
                            if (!th.imageSelected) {
                                th.$emit('sel-image', response.data.id);
                            }
                            th.$emit('set-images-ids', newImagesIds);
                        }
                    })
                    .catch(function (error) {
                        if (error.response) {
                            var respData = error.response.data;
                            if (_.isObject(respData)) {
                                th.progressBars[itemBarNum] = respData['non_field_errors'] || respData['detail']  || itemDict.checkFields;
                            }
                        } else if (error.request) {
                            console.log(error.request);
                        } else {
                            console.log('Error', error.message);
                        }
                    });
                })(this.progressBars.length-1);

            }
        },
        refreshImages: function () {
            var th = this;
            if (th.imagesIds.length) {
                axios({
                    method: 'GET', url: '/image/api/',
                    headers: { 'X-CSRFToken': _gl.getCSRFToken() },
                    params: { 'ids': th.imagesIds.join(',') },
                }).then(function (response) {
                   th.images = response.data;
                });
            } else {
                th.images = [];
            }
        },
        selectImg: function () {
            this.$el.querySelector(".imgf").click();
        },
        previewImg: function (fileName) {
            return _gl.makeResizePath(fileName, 's_100x100');
        },
        actImg: function (id, act) {
            var th = this;
            axios({
                method: 'POST',
                url: "/image/api/"+id+"/"+act+"/",
                headers: { 'X-CSRFToken': _gl.getCSRFToken() },
            }).then(function (response) {
               th.refreshImages();
            });
        },
        actDel: function (id) {
            var th = this;
            axios({
                method: 'DELETE', url: "/image/api/"+id+"/",
                headers: { 'X-CSRFToken': _gl.getCSRFToken() },
            }).then(function (response) {
                var newImagesIds = _.clone(th.imagesIds)
                newImagesIds = _.without(newImagesIds, id)
                if (th.imageSelected == id) {
                    th.$emit('sel-image', _.first(newImagesIds));
                }
                th.$emit('set-images-ids', newImagesIds);
            });


        },
        actSel: function (id) {
            this.$emit('sel-image', id);
        },
        open: function (img) {
            window.open(img, "Image");
        }

    },
    watch: {
        imagesIds: function (n, o) {
            this.refreshImages();
        }
    },
    mounted: function () {

        if (_.size(this.imagesIds) && !_.contains(this.imagesIds, this.imageSelected)) {
            this.$emit('sel-image', _.first(this.imagesIds));
        }

        this.refreshImages();
    },
    delimiters: ['[[', ']]'],
    template: '#uploads-form-template',
});


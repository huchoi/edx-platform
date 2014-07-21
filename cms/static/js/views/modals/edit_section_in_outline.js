/**
 * The EditXBlockModal is a Backbone view that shows an xblock editor in a modal window.
 * It is invoked using the edit method which is passed an existing rendered xblock,
 * and upon save an optional refresh function can be invoked to update the display.
 */
define(['jquery', 'underscore', 'gettext', 'js/views/modals/base_modal',
    'date', 'js/views/utils/xblock_utils', 'js/collections/course_grader',
    'js/utils/get_date'
],
    function(
        $, _, gettext, BaseModal, date, XBlockViewUtils,
        CourseGraderCollection, DateUtils
    ) {
        'use strict';
        var EditSectionXBlockModal = BaseModal.extend({
            events : {
                'click .action-save': 'save',
                'click .action-modes a': 'changeMode',
                'click .remove-date': 'clearDueDate',
                'click .sync-date': 'clearReleaseDate'
            },

            options: $.extend({}, BaseModal.prototype.options, {
                modalName: 'edit-xblock',
                addSaveButton: true,
                modalSize: 'large'
            }),

            initialize: function() {
                BaseModal.prototype.initialize.call(this);
                this.events = _.extend({}, BaseModal.prototype.events, this.events);
                this.template = this.loadTemplate('edit-section-xblock-modal');
                this.xblockInfo = this.options.model;
                this.graderTypes = new CourseGraderCollection(
                    JSON.parse(this.xblockInfo.get('course_graders')),
                    { parse:true }
                );
                this.options.title = this.getTitle();
            },

            getTitle: function () {
                if (this.model.isChapter()) {
                    return gettext('Section Settings');
                } else if (this.model.isSequential()) {
                    return gettext('Subsection Settings');
                } else {
                    return '';
                }
            },

            getDateTime: function(datetime) {
                // @TODO fix for i18n. Can we get Date in appropriate  format
                // from the server?
                datetime = datetime.split(' at ');
                return {
                    'date': date.parse(datetime[0]).toString('MM/dd/yy'),
                    // @TODO Fix `.split('UTC')` for i18n. Can we get Date in
                    // appropriate  format from the server?
                    'time': date.parse(datetime[1].split('UTC')[0]).toString('hh:mm')
                };
            },

            getContentHtml: function() {
                return this.template({
                    xblockInfo: this.xblockInfo,
                    releaseDate: this.processDate(this.xblockInfo.get('release_date')),
                    dueDate: this.processDate(this.xblockInfo.get('due_date')),
                    graderTypes: this.graderTypes
                });
            },

            processDate: function (value) {
                var datetime = this.getDateTime(value);

                if (!value) {
                    datetime.time = datetime.date = null;
                }

                return datetime;
            },

            render: function() {
                BaseModal.prototype.render.apply(this, arguments);
                this.initializePickers();
                this.setGradingType(this.xblockInfo.get('format'));
            },

            save: function(event) {
                event.preventDefault();
                XBlockViewUtils.updateXBlockFields(
                    this.xblockInfo,
                    {
                        // @TODO check hot it will works with sections.
                        metadata: {
                            'release_date': this.getReleaseDate(),
                            'due_date': this.getDueDate()
                        },
                        // @TODO check hot it will works with sections.
                        graderType: this.getGradingType()
                    }, true
                ).done(this.options.onSave);
                this.hide();
            },

            getDueDate: function () {
                return DateUtils(this.$('#due_date'), this.$('#due_time'));
            },

            getReleaseDate: function () {
                return DateUtils(this.$('#start_date'), this.$('#start_time'));
            },

            setGradingType: function (value) {
                this.$('#grading_type').val(value);
            },

            getGradingType: function () {
                return this.$('#grading_type').val();
            },

            initializePickers: function () {
                this.$('.date').datepicker({'dateFormat': 'm/d/yy'});
                this.$('.time').timepicker({'timeFormat' : 'H:i'});
            },

            clearDueDate: function (event) {
                event.preventDefault();
                this.$('#due_time, #due_date').val('');
            },

            clearReleaseDate:function (event) {
                event.preventDefault();
                this.$('#start_time, #start_date').val('');
            },
        });

        return EditSectionXBlockModal;
    });

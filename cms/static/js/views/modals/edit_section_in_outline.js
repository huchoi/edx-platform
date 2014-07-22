/**
 * The EditXBlockModal is a Backbone view that shows an xblock editor in a modal window.
 * It is invoked using the edit method which is passed an existing rendered xblock,
 * and upon save an optional refresh function can be invoked to update the display.
 */
define(['jquery', 'backbone', 'underscore', 'gettext', 'js/views/modals/base_modal',
    'date', 'js/views/utils/xblock_utils',
    'js/utils/get_date'
],
    function(
        $, Backbone, _, gettext, BaseModal, date, XBlockViewUtils, DateUtils
    ) {
        'use strict';
        var EditSectionXBlockModal, BaseDateView, ReleaseDateView, DueDateView,
            GradingView;

        EditSectionXBlockModal = BaseModal.extend({
            events : {
                'click .action-save': 'save',
                'click .action-modes a': 'changeMode'
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
                this.options.title = this.getTitle();
                this.initializeComponents();
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

            getContentHtml: function() {
                return this.template(this.getContext());
            },

            afterRender: function() {
                BaseModal.prototype.render.apply(this, arguments);
                this.invokeComponentMethod('afterRender');
            },

            save: function(event) {
                event.preventDefault();
                var requestData = _.extend({}, this.getData(), {
                    metadata: this.xblockInfo.convertFieldNames(this.getMetadata())
                });
                XBlockViewUtils.updateXBlockFields(
                    this.xblockInfo, requestData, true
                ).done(this.options.onSave);
                this.hide();
            },

            invokeComponentMethod: function (methodName) {
                var values = _.map(this.components, function (component) {
                    if (_.isFunction(component[methodName])) {
                        return component[methodName]();
                    }
                });

                return _.extend.apply(this, [{}].concat(values));
            },

            getContext: function () {
                return _.extend({
                    xblockInfo: this.xblockInfo
                }, this.invokeComponentMethod('getContext'));
            },

            getData: function () {
                return this.invokeComponentMethod('getData');
            },

            getMetadata: function () {
                return this.invokeComponentMethod('getMetadata');
            },

            initializeComponents: function () {
                this.components = [];
                this.components.push(
                    new ReleaseDateView({
                        selector: '.scheduled-date-input',
                        parentView: this,
                        model: this.xblockInfo
                    })
                );

                if (this.xblockInfo.isSequential()) {
                    this.components.push(
                        new DueDateView({
                            selector: '.due-date-input',
                            parentView: this,
                            model: this.xblockInfo
                        }),
                        new GradingView({
                            selector: '.edit-settings-grading',
                            parentView: this,
                            model: this.xblockInfo
                        })
                    );
                }
            }
        });

        BaseDateView = Backbone.View.extend({
            events : {
                'click .clear-date': 'clearValue'
            },

            afterRender: function () {
                this.setElement(this.options.parentView.$(this.options.selector));
                this.$('.date').datepicker({'dateFormat': 'm/d/yy'});
                this.$('.time').timepicker({'timeFormat' : 'H:i'});
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

            processDate: function (value) {
                if (value) {
                    return this.getDateTime(value);
                } else {
                    return {
                        time: null,
                        date: null
                    };
                }
            }
        });

        DueDateView = BaseDateView.extend({
            getValue: function () {
                return DateUtils(this.$('#due_date'), this.$('#due_time'));
            },

            clearValue: function (event) {
                event.preventDefault();
                this.$('#due_time, #due_date').val('');
            },

            getMetadata: function () {
                return {
                    'due_date': this.getValue()
                };
            },

            getContext: function () {
                return {
                    dueDate: this.processDate(this.model.get('due_date'))
                };
            }
        });

        ReleaseDateView = BaseDateView.extend({
            getValue: function () {
                return DateUtils(this.$('#start_date'), this.$('#start_time'));
            },

            clearValue: function (event) {
                event.preventDefault();
                this.$('#start_time, #start_date').val('');
            },

            getMetadata: function () {
                return {
                    'release_date': this.getValue()
                };
            },

            getContext: function () {
                return {
                    releaseDate: this.processDate(this.model.get('release_date'))
                };
            }
        });

        GradingView = Backbone.View.extend({
            afterRender: function () {
                this.setElement(this.options.parentView.$(this.options.selector));
                this.setValue(this.model.get('format'));
            },

            setValue: function (value) {
                this.$('#grading_type').val(value);
            },

            getValue: function () {
                return this.$('#grading_type').val();
            },

            getData: function () {
                return {
                    'graderType': this.getValue()
                };
            },

            getContext: function () {
                return {
                    graderTypes: JSON.parse(this.model.get('course_graders'))
                };
            }
        });

        return EditSectionXBlockModal;
    });

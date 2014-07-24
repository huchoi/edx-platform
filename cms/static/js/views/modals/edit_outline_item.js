/**
 * The EditXBlockModal is a Backbone view that shows an xblock editor in a modal window.
 * It is invoked using the edit method which is passed an existing rendered xblock,
 * and upon save an optional refresh function can be invoked to update the display.
 */
define(['jquery', 'backbone', 'underscore', 'gettext', 'js/views/modals/base_modal',
    'date', 'js/views/utils/xblock_utils', 'js/utils/date_utils'
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
                modalName: 'edit-outline-item',
                modalType: 'edit-settings',
                addSaveButton: true,
                modalSize: 'large'
            }),

            initialize: function() {
                BaseModal.prototype.initialize.call(this);
                this.events = _.extend({}, BaseModal.prototype.events, this.events);
                this.template = this.loadTemplate('edit-outline-item-modal');
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
                var requestData = _.extend({}, this.getRequestData(), {
                    metadata: this.getMetadata()
                });
                XBlockViewUtils.updateXBlockFields(
                    this.model, requestData, true
                ).done(this.options.onSave);
                this.hide();
            },

            /**
             * Call the method on each value in the list. If the element of the
             * list doesn't have such a method it will be skipped.
             * @param {String} methodName The method name needs to be called.
             * @return {Object}
             */
            invokeComponentMethod: function (methodName) {
                var values = _.map(this.components, function (component) {
                    if (_.isFunction(component[methodName])) {
                        return component[methodName].call(component);
                    }
                });

                return _.extend.apply(this, [{}].concat(values));
            },

            /**
             * Return context for the modal.
             * @return {Object}
             */
            getContext: function () {
                return _.extend({
                    xblockInfo: this.model
                }, this.invokeComponentMethod('getContext'));
            },

            /**
             * Return request data.
             * @return {Object}
             */
            getRequestData: function () {
                return this.invokeComponentMethod('getRequestData');
            },

            /**
             * Return metadata for the XBlock.
             * @return {Object}
             */
            getMetadata: function () {
                return this.invokeComponentMethod('getMetadata');
            },

            /**
             * Initialize internal components.
             */
            initializeComponents: function () {
                this.components = [];
                this.components.push(
                    new ReleaseDateView({
                        selector: '.scheduled-date-input',
                        parentView: this,
                        model: this.model
                    })
                );

                if (this.model.isSequential()) {
                    this.components.push(
                        new DueDateView({
                            selector: '.due-date-input',
                            parentView: this,
                            model: this.model
                        }),
                        new GradingView({
                            selector: '.edit-settings-grading',
                            parentView: this,
                            model: this.model
                        })
                    );
                }
            }
        });

        BaseDateView = Backbone.View.extend({
            // Attribute name in the model
            fieldName: null,

            events : {
                'click .clear-date': 'clearValue'
            },

            afterRender: function () {
                this.setElement(this.options.parentView.$(this.options.selector).get(0));
                this.$('input.date').datepicker({'dateFormat': 'm/d/yy'});
                this.$('input.time').timepicker({
                    'timeFormat' : 'H:i',
                    'forceRoundTime': true
                });
                if (this.model.get(this.fieldName)) {
                    DateUtils.setDate(
                        this.$('input.date'), this.$('input.time'),
                        this.model.get(this.fieldName)
                    );
                }
            }
        });

        DueDateView = BaseDateView.extend({
            fieldName: 'due',

            getValue: function () {
                return DateUtils.getDate(this.$('#due_date'), this.$('#due_time'));
            },

            clearValue: function (event) {
                event.preventDefault();
                this.$('#due_time, #due_date').val('');
            },

            getMetadata: function () {
                return {
                    'due': this.getValue()
                };
            }
        });

        ReleaseDateView = BaseDateView.extend({
            fieldName: 'start',

            getValue: function () {
                return DateUtils.getDate(this.$('#start_date'), this.$('#start_time'));
            },

            clearValue: function (event) {
                event.preventDefault();
                this.$('#start_time, #start_date').val('');
            },

            getMetadata: function () {
                return {
                    'start': this.getValue()
                };
            }
        });

        GradingView = Backbone.View.extend({
            afterRender: function () {
                this.setElement(this.options.parentView.$(this.options.selector).get(0));
                this.setValue(this.model.get('format'));
            },

            setValue: function (value) {
                this.$('#grading_type').val(value);
            },

            getValue: function () {
                return this.$('#grading_type').val();
            },

            getRequestData: function () {
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
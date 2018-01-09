#!/usr/bin/env ruby

require 'rake'
require 'rspec/core/rake_task'

task :default => :spec

require 'rake'
require 'rspec/core/rake_task'
require 'yaml'

properties = YAML.load_file('serverspec_properties.yml')

desc "Run serverspec against all hosts"
task :spec => 'serverspec:all'

namespace :serverspec do

  task :all => properties.keys.map {|key| 'serverspec:' + key.split('.')[0] }
  properties.keys.each do |key|
    desc "Run serverspec to #{key}"
    RSpec::Core::RakeTask.new(key.split('.')[0].to_sym) do |t|
      ENV['TARGET_HOST'] = key
      print "target - #{key}\n\n"
      t.pattern = 'spec/{' + properties[key][:roles].join(',') + '}/*_spec.rb'
    end
   end
end
